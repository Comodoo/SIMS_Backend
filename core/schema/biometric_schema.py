"""
GraphQL types for biometric operations (WebAuthn + face recognition).
"""
import strawberry
from typing import Optional
from datetime import datetime


@strawberry.type
class BiometricStatus:
    """Whether a user has registered biometric credentials."""
    has_webauthn: bool
    has_face: bool
    user_id: strawberry.ID


@strawberry.type
class FaceIdentifyResult:
    """Result of a face-scan identify attempt."""
    success: bool
    message: str
    student_id: Optional[strawberry.ID] = None
    student_name: Optional[str] = None
    confidence: float = 0.0


@strawberry.type
class EnrollmentTokenInfo:
    """Public info returned when resolving a magic-link enrollment token."""
    valid: bool
    message: str
    token: Optional[str] = None
    user_id: Optional[strawberry.ID] = None
    user_name: Optional[str] = None          # full name to display
    enrollment_type: Optional[str] = None    # 'fingerprint' | 'face' | 'both'
    expires_at: Optional[datetime] = None


@strawberry.type
class GenerateTokenResult:
    """Result of generating an enrollment link."""
    success: bool
    message: str
    token: Optional[str] = None
    enrollment_url: Optional[str] = None     # full URL admin can share
