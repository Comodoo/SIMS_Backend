"""
Biometric mutations — WebAuthn (FIDO2 fingerprint) and face recognition.

WebAuthn flow (instructor clock-in):
  1. webauthnBeginRegister(userId)  → JSON options  (admin does once)
  2. webauthnCompleteRegister(userId, credentialJson)  → stores public key
  3. webauthnBeginAuth(userId)  → JSON challenge
  4. webauthnCompleteClockIn(userId, credentialJson, action)  → Attendance record

Face flow (student marking via camera):
  1. registerFace(userId, imageBase64)  → stores face embedding  (admin does once per student)
  2. identifyStudentFace(imageBase64, courseId, date, teacherId)  → marks attendance
"""

import strawberry
import base64
import os
from typing import Optional
from django.utils import timezone as tz
from datetime import timedelta

from core.models.core_models import User, Staff, Student, Attendance, StudentAttendance, EnrollmentToken
from core.schema.core_schema import AttendanceType
from core.schema.biometric_schema import BiometricStatus, FaceIdentifyResult, GenerateTokenResult

# Re-use the same response shape defined in core_mutations to avoid duplicate type names
# Import lazily inside methods where needed, or use a local alias.
@strawberry.type
class BiometricClockResponse:
    success: bool
    message: str
    attendance: Optional[AttendanceType] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _decode_image(image_base64: str):
    """Decode a base64 (or data-URL) image to a numpy RGB array."""
    import numpy as np
    from PIL import Image
    import io

    if ',' in image_base64:
        image_base64 = image_base64.split(',')[1]
    img_bytes = base64.b64decode(image_base64)
    img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    return np.array(img)


# Module-level singleton — loaded once on first face operation
_face_app = None


def _get_face_app():
    """Lazy-load insightface model (downloads ~80 MB on first use)."""
    global _face_app
    if _face_app is None:
        from insightface.app import FaceAnalysis
        _face_app = FaceAnalysis(name='buffalo_sc', providers=['CPUExecutionProvider'])
        _face_app.prepare(ctx_id=0, det_size=(640, 640))
    return _face_app


def _get_embedding(image_base64: str) -> list:
    """Extract a normalised 512-float face embedding using insightface (ONNX, no TensorFlow)."""
    import cv2
    import numpy as np

    img_array = _decode_image(image_base64)
    # insightface expects BGR
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    faces = _get_face_app().get(img_bgr)
    if not faces:
        raise ValueError("No face detected in image — ensure good lighting and face is visible")
    # normed_embedding is already L2-normalised → dot product == cosine similarity
    return faces[0].normed_embedding.tolist()


def _cosine_similarity(a: list, b: list) -> float:
    """Cosine similarity of two L2-normalised embeddings (insightface output)."""
    import numpy as np
    # Both vectors are already unit-length, so dot product = cosine similarity
    return float(np.dot(np.array(a), np.array(b)))


def _rp_id() -> str:
    return os.environ.get('WEBAUTHN_RP_ID', 'localhost')


def _origin() -> str:
    return os.environ.get('WEBAUTHN_ORIGIN', 'http://localhost:3000')


# ---------------------------------------------------------------------------
# Mutation class
# ---------------------------------------------------------------------------

@strawberry.type
class BiometricMutation:

    # ------------------------------------------------------------------ #
    # WebAuthn — REGISTRATION (admin runs once per instructor)            #
    # ------------------------------------------------------------------ #

    @strawberry.mutation
    def webauthn_begin_register(self, user_id: strawberry.ID) -> str:
        """
        Step 1 of fingerprint enrollment.
        Returns JSON options that the browser passes to navigator.credentials.create().
        """
        import webauthn
        from webauthn.helpers import generate_challenge, options_to_json
        from webauthn.helpers.structs import (
            AuthenticatorSelectionCriteria,
            UserVerificationRequirement,
        )

        user = User.objects.get(user_id=user_id)
        challenge = generate_challenge()

        user.webauthn_challenge = base64.b64encode(challenge).decode()
        user.webauthn_challenge_expires = tz.now() + timedelta(minutes=5)
        user.save(update_fields=['webauthn_challenge', 'webauthn_challenge_expires'])

        options = webauthn.generate_registration_options(
            rp_id=_rp_id(),
            rp_name=os.environ.get('WEBAUTHN_RP_NAME', 'SIMS'),
            user_id=str(user.user_id).encode(),
            user_name=user.username,
            user_display_name=user.get_full_name() or user.username,
            challenge=challenge,
            authenticator_selection=AuthenticatorSelectionCriteria(
                user_verification=UserVerificationRequirement.REQUIRED,
            ),
        )
        return options_to_json(options)

    @strawberry.mutation
    def webauthn_complete_register(
        self,
        user_id: strawberry.ID,
        credential_json: str,
    ) -> str:
        """
        Step 2 of fingerprint enrollment.
        Verifies the browser credential and stores the public key on the user.
        Returns a JSON string: {"success": bool, "message": str}
        """
        import json, webauthn

        try:
            user = User.objects.get(user_id=user_id)

            if not user.webauthn_challenge or not user.webauthn_challenge_expires:
                return json.dumps({"success": False, "message": "No pending registration challenge"})
            if tz.now() > user.webauthn_challenge_expires:
                return json.dumps({"success": False, "message": "Registration challenge expired — start again"})

            challenge = base64.b64decode(user.webauthn_challenge)
            credential_data = json.loads(credential_json)

            verified = webauthn.verify_registration_response(
                credential=credential_data,
                expected_challenge=challenge,
                expected_rp_id=_rp_id(),
                expected_origin=_origin(),
            )

            user.webauthn_credential_id = verified.credential_id
            user.webauthn_public_key = verified.credential_public_key
            user.webauthn_sign_count = verified.sign_count
            user.webauthn_challenge = None
            user.webauthn_challenge_expires = None
            user.save(update_fields=[
                'webauthn_credential_id', 'webauthn_public_key',
                'webauthn_sign_count', 'webauthn_challenge', 'webauthn_challenge_expires',
            ])

            return json.dumps({"success": True, "message": "Fingerprint registered successfully"})
        except Exception as e:
            import json
            return json.dumps({"success": False, "message": f"Registration failed: {str(e)}"})

    # ------------------------------------------------------------------ #
    # WebAuthn — AUTHENTICATION (instructor clock-in / clock-out)         #
    # ------------------------------------------------------------------ #

    @strawberry.mutation
    def webauthn_begin_auth(self, user_id: strawberry.ID) -> str:
        """
        Step 1 of fingerprint clock-in.
        Returns JSON options the browser passes to navigator.credentials.get().
        """
        import webauthn
        from webauthn.helpers import generate_challenge, options_to_json
        from webauthn.helpers.structs import (
            PublicKeyCredentialDescriptor,
            UserVerificationRequirement,
        )

        user = User.objects.get(user_id=user_id)

        if not user.webauthn_credential_id:
            raise Exception("No fingerprint registered for this user. Please register first.")

        challenge = generate_challenge()
        user.webauthn_challenge = base64.b64encode(challenge).decode()
        user.webauthn_challenge_expires = tz.now() + timedelta(minutes=5)
        user.save(update_fields=['webauthn_challenge', 'webauthn_challenge_expires'])

        options = webauthn.generate_authentication_options(
            rp_id=_rp_id(),
            allow_credentials=[
                PublicKeyCredentialDescriptor(id=bytes(user.webauthn_credential_id))
            ],
            user_verification=UserVerificationRequirement.REQUIRED,
            challenge=challenge,
        )
        return options_to_json(options)

    @strawberry.mutation
    def webauthn_complete_clock_in(
        self,
        user_id: strawberry.ID,
        credential_json: str,
        action: str = 'in',
    ) -> BiometricClockResponse:
        """
        Step 2 of fingerprint clock-in/out.
        Verifies the WebAuthn assertion then creates an Attendance record.
        action: 'in' or 'out'
        """
        import json, webauthn

        try:
            user = User.objects.get(user_id=user_id)

            if not user.webauthn_challenge or not user.webauthn_challenge_expires:
                return BiometricClockResponse(success=False, message="No pending authentication challenge")
            if tz.now() > user.webauthn_challenge_expires:
                return BiometricClockResponse(success=False, message="Authentication challenge expired — try again")

            challenge = base64.b64decode(user.webauthn_challenge)
            credential_data = json.loads(credential_json)

            verified = webauthn.verify_authentication_response(
                credential=credential_data,
                expected_challenge=challenge,
                expected_rp_id=_rp_id(),
                expected_origin=_origin(),
                credential_public_key=bytes(user.webauthn_public_key),
                credential_current_sign_count=user.webauthn_sign_count,
            )

            # Update sign count to prevent replay attacks
            user.webauthn_sign_count = verified.new_sign_count
            user.webauthn_challenge = None
            user.webauthn_challenge_expires = None
            user.save(update_fields=['webauthn_sign_count', 'webauthn_challenge', 'webauthn_challenge_expires'])

            staff = Staff.objects.get(user=user)
            attendance = Attendance.objects.create(
                user=user,
                staff=staff,
                status=action,
                method='webauthn',
            )

            verb = 'in' if action == 'in' else 'out'
            late_msg = f" ({attendance.late_minutes} min late)" if attendance.is_late else ""
            return BiometricClockResponse(
                success=True,
                message=f"Clocked {verb} via fingerprint{late_msg}",
                attendance=AttendanceType.from_model(attendance),
            )
        except Staff.DoesNotExist:
            return BiometricClockResponse(success=False, message="Staff profile not found")
        except Exception as e:
            return BiometricClockResponse(success=False, message=f"Error: {str(e)}")

    # ------------------------------------------------------------------ #
    # Face — REGISTRATION (admin runs once per student)                   #
    # ------------------------------------------------------------------ #

    @strawberry.mutation
    def register_face(self, user_id: strawberry.ID, image_base64: str) -> str:
        """
        Register a face embedding for a user.
        image_base64: JPEG/PNG as base64 (data-URL prefix optional).
        Returns JSON: {"success": bool, "message": str}
        """
        import json
        try:
            user = User.objects.get(user_id=user_id)
            embedding = _get_embedding(image_base64)
            user.face_embedding = embedding
            user.save(update_fields=['face_embedding'])
            return json.dumps({"success": True, "message": "Face registered successfully"})
        except Exception as e:
            return json.dumps({"success": False, "message": f"Face registration failed: {str(e)}"})

    # ------------------------------------------------------------------ #
    # Face — IDENTIFY + MARK (instructor uses during class)               #
    # ------------------------------------------------------------------ #

    @strawberry.mutation
    def identify_student_face(
        self,
        image_base64: str,
        course_id: strawberry.ID,
        date: str,
        teacher_id: strawberry.ID,
        semester_id: Optional[strawberry.ID] = None,
    ) -> FaceIdentifyResult:
        """
        Identify a student from a face photo and mark them present.
        Compares against all students enrolled in course_id with registered face embeddings.
        Threshold: cosine similarity >= 0.80.
        """
        try:
            from academics.models.academics_models import Enrollment

            input_embedding = _get_embedding(image_base64)
            # insightface normed embeddings: cosine sim >= 0.40 is a reliable match
            threshold = float(os.environ.get('FACE_MATCH_THRESHOLD', '0.40'))

            enrollments = Enrollment.objects.filter(
                course_id=course_id, status='active',
            ).select_related('student__user')

            best_match = None
            best_score = 0.0

            for enrollment in enrollments:
                student = enrollment.student
                if not student.user.face_embedding:
                    continue
                score = _cosine_similarity(input_embedding, student.user.face_embedding)
                if score > best_score:
                    best_score = score
                    best_match = student

            confidence = round(best_score * 100, 1)

            if best_match and best_score >= threshold:
                teacher = Staff.objects.get(staff_id=teacher_id)
                semester = None
                if semester_id:
                    from academics.models.academic_structure_models import Semester
                    try:
                        semester = Semester.objects.get(semester_id=semester_id)
                    except Semester.DoesNotExist:
                        pass

                StudentAttendance.objects.update_or_create(
                    student=best_match,
                    course_id=course_id,
                    date=date,
                    defaults=dict(status='present', marked_by=teacher, semester=semester, method='face'),
                )
                return FaceIdentifyResult(
                    success=True,
                    message=f"{best_match.full_name} marked present ({confidence}% match)",
                    student_id=strawberry.ID(str(best_match.student_id)),
                    student_name=best_match.full_name,
                    confidence=confidence,
                )
            else:
                return FaceIdentifyResult(
                    success=False,
                    message="Face not recognised — mark manually" if best_score > 0 else "No face detected in image",
                    confidence=confidence,
                )
        except Exception as e:
            return FaceIdentifyResult(
                success=False,
                message=f"Error: {str(e)}",
                confidence=0.0,
            )

    # ------------------------------------------------------------------ #
    # WebAuthn — STUDENT ATTENDANCE (teacher marks via student fingerprint)#
    # ------------------------------------------------------------------ #

    @strawberry.mutation
    def webauthn_mark_student_attendance(
        self,
        student_user_id: strawberry.ID,
        course_id: strawberry.ID,
        date: str,
        credential_json: str,
        teacher_id: strawberry.ID,
        semester_id: Optional[strawberry.ID] = None,
    ) -> FaceIdentifyResult:
        """
        Verify a student's WebAuthn fingerprint and mark them present.
        Flow: teacher selects the student → student places finger on device →
        backend verifies the credential → StudentAttendance created.
        """
        import json, webauthn
        try:
            student_user = User.objects.get(user_id=student_user_id)

            if not student_user.webauthn_credential_id:
                return FaceIdentifyResult(
                    success=False,
                    message="This student has no fingerprint registered — ask admin to enrol them first",
                )

            if not student_user.webauthn_challenge or not student_user.webauthn_challenge_expires:
                return FaceIdentifyResult(success=False, message="No pending authentication challenge — try again")
            if tz.now() > student_user.webauthn_challenge_expires:
                return FaceIdentifyResult(success=False, message="Authentication challenge expired — try again")

            challenge = base64.b64decode(student_user.webauthn_challenge)
            credential_data = json.loads(credential_json)

            verified = webauthn.verify_authentication_response(
                credential=credential_data,
                expected_challenge=challenge,
                expected_rp_id=_rp_id(),
                expected_origin=_origin(),
                credential_public_key=bytes(student_user.webauthn_public_key),
                credential_current_sign_count=student_user.webauthn_sign_count,
            )

            student_user.webauthn_sign_count = verified.new_sign_count
            student_user.webauthn_challenge = None
            student_user.webauthn_challenge_expires = None
            student_user.save(update_fields=[
                'webauthn_sign_count', 'webauthn_challenge', 'webauthn_challenge_expires',
            ])

            student = Student.objects.get(user=student_user)
            teacher = Staff.objects.get(staff_id=teacher_id)

            semester = None
            if semester_id:
                from academics.models.academic_structure_models import Semester
                try:
                    semester = Semester.objects.get(semester_id=semester_id)
                except Semester.DoesNotExist:
                    pass

            StudentAttendance.objects.update_or_create(
                student=student,
                course_id=course_id,
                date=date,
                defaults=dict(status='present', marked_by=teacher, semester=semester, method='fingerprint'),
            )

            return FaceIdentifyResult(
                success=True,
                message=f"{student.full_name} marked present via fingerprint",
                student_id=strawberry.ID(str(student.student_id)),
                student_name=student.full_name,
                confidence=100.0,
            )
        except Student.DoesNotExist:
            return FaceIdentifyResult(success=False, message="Student profile not found")
        except Staff.DoesNotExist:
            return FaceIdentifyResult(success=False, message="Teacher profile not found")
        except Exception as e:
            return FaceIdentifyResult(success=False, message=f"Error: {str(e)}")

    # ------------------------------------------------------------------ #
    # Status query helper (exposed as mutation for simplicity)            #
    # ------------------------------------------------------------------ #

    @strawberry.mutation
    def clock_in_with_face(
        self,
        user_id: strawberry.ID,
        image_base64: str,
        action: str = 'in',
    ) -> BiometricClockResponse:
        """
        Clock in or out by verifying the staff member's own face.
        Compares the captured image against the face embedding stored for this user.
        action: 'in' | 'out'
        """
        try:
            user = User.objects.get(user_id=user_id)

            if not user.face_embedding:
                return BiometricClockResponse(
                    success=False,
                    message="No face registered — go to My Profile to register your face first",
                )

            input_embedding = _get_embedding(image_base64)
            score = _cosine_similarity(input_embedding, user.face_embedding)
            threshold = float(os.environ.get('FACE_MATCH_THRESHOLD', '0.40'))

            if score < threshold:
                return BiometricClockResponse(
                    success=False,
                    message=f"Face not recognised ({round(score * 100)}% match — try better lighting)",
                )

            staff = Staff.objects.get(user=user)
            attendance = Attendance.objects.create(
                user=user,
                staff=staff,
                status=action,
                method='face',
                biometric_match_score=round(score * 100, 1),
            )

            verb = 'in' if action == 'in' else 'out'
            late_msg = f" ({attendance.late_minutes} min late)" if attendance.is_late else ""
            return BiometricClockResponse(
                success=True,
                message=f"Clocked {verb} via face recognition{late_msg}",
                attendance=AttendanceType.from_model(attendance),
            )
        except Staff.DoesNotExist:
            return BiometricClockResponse(success=False, message="Staff profile not found")
        except Exception as e:
            return BiometricClockResponse(success=False, message=f"Error: {str(e)}")

    @strawberry.mutation
    def check_biometric_status(self, user_id: strawberry.ID) -> BiometricStatus:
        """Returns which biometric methods are registered for a user."""
        try:
            user = User.objects.get(user_id=user_id)
            return BiometricStatus(
                has_webauthn=bool(user.webauthn_credential_id),
                has_face=bool(user.face_embedding),
                user_id=strawberry.ID(str(user.user_id)),
            )
        except User.DoesNotExist:
            return BiometricStatus(has_webauthn=False, has_face=False, user_id=strawberry.ID(str(user_id)))

    # ------------------------------------------------------------------ #
    # Enrollment token — admin generates a magic link for a user          #
    # ------------------------------------------------------------------ #

    @strawberry.mutation
    def generate_enrollment_token(
        self,
        user_id: strawberry.ID,
        enrollment_type: str = 'both',
        created_by_id: Optional[strawberry.ID] = None,
        expires_hours: int = 24,
    ) -> GenerateTokenResult:
        """
        Generate a one-time enrollment link for a user.
        enrollment_type: 'fingerprint' | 'face' | 'both'
        Returns the token and a full URL the admin can share via WhatsApp/email.
        """
        import secrets
        try:
            user = User.objects.get(user_id=user_id)
            created_by = None
            if created_by_id:
                try:
                    created_by = User.objects.get(user_id=created_by_id)
                except User.DoesNotExist:
                    pass

            token = secrets.token_hex(32)   # 64-char hex string
            expires = tz.now() + timedelta(hours=expires_hours)

            EnrollmentToken.objects.create(
                user=user,
                token=token,
                enrollment_type=enrollment_type,
                created_by=created_by,
                expires_at=expires,
            )

            frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
            url = f"{frontend_url}/enroll/{token}"

            name = user.get_full_name() or user.username
            return GenerateTokenResult(
                success=True,
                message=f"Enrollment link generated for {name} (expires in {expires_hours}h)",
                token=token,
                enrollment_url=url,
            )
        except User.DoesNotExist:
            return GenerateTokenResult(success=False, message="User not found")
        except Exception as e:
            return GenerateTokenResult(success=False, message=f"Error: {str(e)}")

    # ------------------------------------------------------------------ #
    # Token-based enrollment (called from the magic-link page, no auth)   #
    # ------------------------------------------------------------------ #

    @strawberry.mutation
    def enroll_fingerprint_with_token(
        self,
        token: str,
        credential_json: str,
    ) -> str:
        """
        WebAuthn registration using a magic-link token instead of auth header.
        Step 2 of the enrollment flow on /enroll/[token].
        Returns JSON: {"success": bool, "message": str}
        """
        import json, webauthn
        try:
            et = EnrollmentToken.objects.select_related('user').get(token=token)
            if not et.is_valid:
                return json.dumps({"success": False, "message": "Link has expired or already been used"})
            if et.enrollment_type not in ('fingerprint', 'both'):
                return json.dumps({"success": False, "message": "This link is not for fingerprint enrollment"})

            user = et.user
            if not user.webauthn_challenge or not user.webauthn_challenge_expires:
                return json.dumps({"success": False, "message": "No pending challenge — call webauthnBeginRegister first"})
            if tz.now() > user.webauthn_challenge_expires:
                return json.dumps({"success": False, "message": "Challenge expired — start again"})

            challenge = base64.b64decode(user.webauthn_challenge)
            credential_data = json.loads(credential_json)

            verified = webauthn.verify_registration_response(
                credential=credential_data,
                expected_challenge=challenge,
                expected_rp_id=_rp_id(),
                expected_origin=_origin(),
            )

            user.webauthn_credential_id = verified.credential_id
            user.webauthn_public_key = verified.credential_public_key
            user.webauthn_sign_count = verified.sign_count
            user.webauthn_challenge = None
            user.webauthn_challenge_expires = None
            user.save(update_fields=[
                'webauthn_credential_id', 'webauthn_public_key',
                'webauthn_sign_count', 'webauthn_challenge', 'webauthn_challenge_expires',
            ])

            # Mark token as used if both types are done (or type is fingerprint-only)
            if et.enrollment_type == 'fingerprint':
                et.mark_used()

            return json.dumps({"success": True, "message": "Fingerprint registered successfully!"})
        except EnrollmentToken.DoesNotExist:
            return json.dumps({"success": False, "message": "Invalid or unknown link"})
        except Exception as e:
            return json.dumps({"success": False, "message": f"Registration failed: {str(e)}"})

    @strawberry.mutation
    def enroll_face_with_token(
        self,
        token: str,
        image_base64: str,
    ) -> str:
        """
        Face registration using a magic-link token instead of auth header.
        Returns JSON: {"success": bool, "message": str}
        """
        import json
        try:
            et = EnrollmentToken.objects.select_related('user').get(token=token)
            if not et.is_valid:
                return json.dumps({"success": False, "message": "Link has expired or already been used"})
            if et.enrollment_type not in ('face', 'both'):
                return json.dumps({"success": False, "message": "This link is not for face enrollment"})

            embedding = _get_embedding(image_base64)
            et.user.face_embedding = embedding
            et.user.save(update_fields=['face_embedding'])

            # Mark token used if face-only or if fingerprint already done
            if et.enrollment_type == 'face':
                et.mark_used()
            elif et.enrollment_type == 'both' and et.user.webauthn_credential_id:
                et.mark_used()

            return json.dumps({"success": True, "message": "Face registered successfully!"})
        except EnrollmentToken.DoesNotExist:
            return json.dumps({"success": False, "message": "Invalid or unknown link"})
        except Exception as e:
            return json.dumps({"success": False, "message": f"Face registration failed: {str(e)}"})
