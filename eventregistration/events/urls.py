"""
URL patterns for Django template views (HTML pages).
"""
from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list, name='list'),
    path('<int:pk>/', views.event_detail, name='detail'),
    path('my-registrations/', views.my_registrations, name='my_registrations'),
]
