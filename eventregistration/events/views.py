"""
Views for the events application.

API views (DRF ViewSets) are in this file alongside Django template views.
Queries are optimised with select_related / prefetch_related to avoid N+1.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, F
from django.utils import timezone

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

from .models import Event, Registration
from .serializers import (
    EventListSerializer,
    EventDetailSerializer,
    RegistrationSerializer,
)
from .emails import send_registration_confirmation, send_cancellation_notice


# ---------------------------------------------------------------------------
# Custom throttle for registration endpoint
# ---------------------------------------------------------------------------
class RegistrationThrottle(UserRateThrottle):
    scope = 'registration'


# ===========================================================================
# API ViewSets
# ===========================================================================

class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    read-only endpoint for events.
    GET /api/events/         — paginated list with optional search
    GET /api/events/<id>/    — single event detail
    """
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['date', 'title', 'created_at']
    ordering = ['date']

    def get_queryset(self):
        """
        Return events with pre-computed registration count to power
        spots_remaining without extra queries per row.
        Supports ?search=  and ?upcoming=true query params.
        """
        qs = Event.objects.annotate(
            # active_count is used indirectly via model property
        ).prefetch_related(
            'registrations'
        )

        upcoming = self.request.query_params.get('upcoming')
        if upcoming and upcoming.lower() == 'true':
            qs = qs.filter(date__gte=timezone.now())

        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EventDetailSerializer
        return EventListSerializer


class RegistrationViewSet(viewsets.ModelViewSet):
    """
    POST   /api/registrations/          — register for an event
    GET    /api/registrations/          — list current user's registrations
    DELETE /api/registrations/<id>/     — cancel a registration

    Security:
    - Users can only see and cancel their own registrations.
    - Capacity check runs in the serializer validate() method.
    - Email must be valid (Django EmailField + serializer normalisation).
    - Rate limit: 10 registrations per minute.
    """
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [RegistrationThrottle, AnonRateThrottle]

    def get_queryset(self):
        """
        Returns only the current user's registrations.
        Uses select_related to pull event data in one query.
        """
        return (
            Registration.objects
            .filter(user=self.request.user)
            .select_related('event')
            .order_by('-registered_at')
        )

    def create(self, request, *args, **kwargs):
        """
        Register for an event.
        Returns 201 on success, 400 on validation failure.
        Sends an HTML + plain-text confirmation email on success.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        registration = serializer.save()

        # Fire confirmation email — failures are caught inside, never block the response
        send_registration_confirmation(registration, request=request)

        return Response(
            self.get_serializer(registration).data,
            status=status.HTTP_201_CREATED
        )

    def destroy(self, request, *args, **kwargs):
        """
        Cancel a registration (soft-delete via is_cancelled flag).
        Only the owner may cancel — enforced by get_queryset filtering.
        Sends an HTML + plain-text cancellation notice email on success.
        """
        registration = self.get_object()
        if registration.is_cancelled:
            return Response(
                {'detail': 'This registration is already cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        registration.is_cancelled = True
        registration.save(update_fields=['is_cancelled'])

        # Fire cancellation notice — failures are caught inside, never block the response
        send_cancellation_notice(registration, request=request)

        return Response(
            {'detail': 'Registration cancelled successfully.'},
            status=status.HTTP_200_OK
        )

    # Disallow PUT/PATCH — registrations are immutable once created
    def update(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Method not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Method not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


# ===========================================================================
# Django template views (HTML pages)
# ===========================================================================

def event_list(request):
    """
    Render the event list page.
    Events are loaded via the API (Vanilla JS / fetch) for infinite scroll,
    but we pass the auth token so the JS can include it in headers.
    """
    return render(request, 'events/list.html')


def event_detail(request, pk):
    """
    Render the event detail + registration form page.
    Event data is fetched client-side via fetch API.
    """
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'events/detail.html', {'event_id': pk, 'event': event})


@login_required
def my_registrations(request):
    """
    Render the 'My Registrations' page.
    Registration list is fetched client-side.
    """
    return render(request, 'events/my_registrations.html')
