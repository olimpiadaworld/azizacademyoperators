from datetime import timedelta
from functools import wraps
import os
import jwt
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from .models import AppUser


def _parse_duration(value, default_seconds):
    text = str(value or '').strip().lower()
    try:
        if text.endswith('m'):
            return timedelta(minutes=int(text[:-1]))
        if text.endswith('h'):
            return timedelta(hours=int(text[:-1]))
        if text.endswith('d'):
            return timedelta(days=int(text[:-1]))
        return timedelta(seconds=int(text))
    except Exception:
        return timedelta(seconds=default_seconds)


def verify_password(password, stored_hash):
    if not stored_hash:
        return False
    try:
        if stored_hash.startswith(('pbkdf2_', 'argon2', 'bcrypt')):
            return check_password(password, stored_hash)
    except Exception:
        pass
    # Legacy Node bcryptjs support ($2a$, $2b$) when bcrypt package is installed.
    try:
        import bcrypt
        return bcrypt.checkpw(str(password).encode('utf-8'), str(stored_hash).encode('utf-8'))
    except Exception:
        return False


def issue_tokens(user):
    now = timezone.now()
    access_exp = now + _parse_duration(settings.ACCESS_TOKEN_EXPIRES_IN, 1800)
    refresh_exp = now + _parse_duration(settings.REFRESH_TOKEN_EXPIRES_IN, 7 * 86400)
    payload = {'userId': user.id, 'role': user.role, 'type': 'access', 'iat': int(now.timestamp()), 'exp': int(access_exp.timestamp())}
    refresh_payload = {'userId': user.id, 'role': user.role, 'type': 'refresh', 'iat': int(now.timestamp()), 'exp': int(refresh_exp.timestamp())}
    return {
        'access': jwt.encode(payload, settings.JWT_ACCESS_SECRET, algorithm='HS256'),
        'refresh': jwt.encode(refresh_payload, settings.JWT_REFRESH_SECRET, algorithm='HS256'),
    }


def authenticate_request(request):
    header = request.headers.get('Authorization', '')
    if not header.startswith('Bearer '):
        return None
    token = header.split(' ', 1)[1].strip()
    try:
        payload = jwt.decode(token, settings.JWT_ACCESS_SECRET, algorithms=['HS256'])
        if payload.get('type') != 'access':
            return None
        return AppUser.objects.filter(id=payload.get('userId'), is_active=True).first()
    except Exception:
        return None


def require_auth(*roles):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            user = authenticate_request(request)
            if not user:
                return JsonResponse({'detail': 'Autentifikatsiya kerak.'}, status=401)
            if roles and user.role not in roles:
                return JsonResponse({'detail': 'Ruxsat yo‘q.'}, status=403)
            request.app_user = user
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def decode_refresh(token):
    payload = jwt.decode(token, settings.JWT_REFRESH_SECRET, algorithms=['HS256'])
    if payload.get('type') != 'refresh':
        raise ValueError('Wrong token type')
    return payload
