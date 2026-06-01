"""
File upload endpoint for assignment submissions.
"""
import os
import uuid
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx',
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp',
    'txt', 'csv', 'zip', 'rar', '7z',
    'mp4', 'avi', 'mov', 'mkv', 'mp3', 'wav',
    'py', 'js', 'ts', 'java', 'c', 'cpp', 'html', 'css',
}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


def _get_user(request):
    """Resolve authenticated user from Bearer token (token == user_id UUID)."""
    from core.models.core_models import User
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        token = auth[7:].strip()
    else:
        token = auth.strip()
    if not token:
        return None
    try:
        return User.objects.get(user_id=token, is_active=True)
    except User.DoesNotExist:
        return None


@method_decorator(csrf_exempt, name='dispatch')
class UploadFileView(View):
    """Accept a multipart file upload, save to media/submissions/, return URL."""

    def post(self, request):
        user = _get_user(request)
        if not user:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        uploaded = request.FILES.get('file')
        if not uploaded:
            return JsonResponse({'error': 'No file provided'}, status=400)

        if uploaded.size > MAX_FILE_SIZE:
            return JsonResponse(
                {'error': f'File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)} MB.'},
                status=400,
            )

        original_name = uploaded.name
        ext = original_name.rsplit('.', 1)[-1].lower() if '.' in original_name else ''
        if ext not in ALLOWED_EXTENSIONS:
            return JsonResponse(
                {'error': f'File type ".{ext}" is not allowed.'},
                status=400,
            )

        # Save with a UUID filename to avoid collisions
        save_name = f"{uuid.uuid4().hex}.{ext}"
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'submissions')
        os.makedirs(upload_dir, exist_ok=True)

        dest_path = os.path.join(upload_dir, save_name)
        with open(dest_path, 'wb+') as dest:
            for chunk in uploaded.chunks():
                dest.write(chunk)

        # Build absolute URL using request so it works on any host/port
        relative_url = f"{settings.MEDIA_URL}submissions/{save_name}"
        absolute_url = request.build_absolute_uri(relative_url)

        return JsonResponse({
            'url': absolute_url,
            'relativeUrl': relative_url,
            'filename': original_name,
            'type': ext,
            'size': uploaded.size,
        })

    def options(self, request, *args, **kwargs):
        """Handle CORS preflight."""
        response = JsonResponse({})
        response['Allow'] = 'POST, OPTIONS'
        return response
