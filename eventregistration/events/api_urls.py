"""
URL patterns for the REST API endpoints.
Mounted under /api/ in the root URLconf.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views

router = DefaultRouter()
router.register(r'events', views.EventViewSet, basename='event')
router.register(r'registrations', views.RegistrationViewSet, basename='registration')

urlpatterns = [
    path('', include(router.urls)),
    # Token auth endpoint: POST /api/token-auth/  → returns {"token": "..."}
    path('token-auth/', obtain_auth_token, name='api_token_auth'),
    # DRF browsable API login/logout (dev convenience)
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]
