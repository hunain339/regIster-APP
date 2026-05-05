"""
Root URL configuration for eventregistration project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Frontend pages (Django-rendered HTML)
    path('', RedirectView.as_view(url='/events/', permanent=False)),
    path('events/', include('events.urls')),

    # REST API endpoints
    path('api/', include('events.api_urls')),
]
