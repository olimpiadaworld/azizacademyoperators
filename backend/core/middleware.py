import time
import uuid
from collections import defaultdict, deque
from django.conf import settings
from django.http import JsonResponse

_RATE_BUCKETS = defaultdict(deque)


def _client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '') or 'unknown'


def _limited(key, limit, window_seconds):
    now = time.time()
    bucket = _RATE_BUCKETS[key]
    while bucket and bucket[0] <= now - window_seconds:
        bucket.popleft()
    if len(bucket) >= limit:
        return True
    bucket.append(now)
    return False


class RequestIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        request.request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        response = self.get_response(request)
        response['X-Request-ID'] = request.request_id
        return response


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        response = self.get_response(request)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['Referrer-Policy'] = 'no-referrer'
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        response['Cross-Origin-Opener-Policy'] = 'same-origin'
        return response


class SimpleCorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed = set(settings.CORS_ALLOWED_ORIGINS)
    def __call__(self, request):
        origin = request.headers.get('Origin', '').rstrip('/')
        if request.method == 'OPTIONS':
            response = JsonResponse({})
        else:
            response = self.get_response(request)
        if origin and (origin in self.allowed or (settings.DEBUG and origin.startswith(('http://localhost:', 'http://127.0.0.1:')))):
            response['Access-Control-Allow-Origin'] = origin
            response['Vary'] = 'Origin'
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type, X-Requested-With'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        return response


class SimpleRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        if request.method == 'OPTIONS' or not request.path.startswith('/api/'):
            return self.get_response(request)
        ip = _client_ip(request)
        path = request.path.rstrip('/') + '/'
        if path.endswith('/api/auth/login/'):
            if _limited(('auth', ip), settings.AUTH_RATE_LIMIT_PER_15_MINUTES, 15 * 60):
                return JsonResponse({'detail': 'Juda ko‘p login urinish. 15 daqiqadan keyin urinib ko‘ring.'}, status=429)
        elif path.endswith('/api/public/online-leads/'):
            if _limited(('public_lead', ip), settings.PUBLIC_LEAD_RATE_LIMIT_PER_MINUTE, 60):
                return JsonResponse({'detail': 'Juda ko‘p so‘rov. Birozdan keyin urinib ko‘ring.'}, status=429)
        else:
            if _limited(('api', ip), settings.API_RATE_LIMIT_PER_MINUTE, 60):
                return JsonResponse({'detail': 'Juda ko‘p so‘rov. Birozdan keyin urinib ko‘ring.'}, status=429)
        return self.get_response(request)
