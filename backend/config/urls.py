from django.urls import path, include
from django.http import JsonResponse


def root(request):
    return JsonResponse({'status': 'ok', 'message': 'Django backend ishlayapti'})

urlpatterns = [
    path('', root),
    path('api/', include('core.urls')),
]
