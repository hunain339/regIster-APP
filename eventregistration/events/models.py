"""
Models for the events application.

Event — represents a schedulable event with capacity management.
Registration — tracks user sign-ups, with cancellation support.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone


class Event(models.Model):
    """
    Represents a public event that users can register for.
    Tracks capacity so registrations can be limited.
    """
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=500)
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Maximum number of attendees allowed."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.date.strftime('%Y-%m-%d')})"

    @property
    def spots_remaining(self):
        """Return how many spots are still available."""
        confirmed = self.registrations.filter(is_cancelled=False).count()
        return max(self.capacity - confirmed, 0)

    @property
    def is_full(self):
        """Return True if no spots remain."""
        return self.spots_remaining == 0

    @property
    def total_registrations(self):
        """Return the count of active (non-cancelled) registrations."""
        return self.registrations.filter(is_cancelled=False).count()


class Registration(models.Model):
    """
    Tracks a user's registration for an Event.
    Soft-deletes via is_cancelled flag rather than hard deletes.
    """
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations'
    )
    # Optionally link to Django user if authenticated
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registrations'
    )
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    is_cancelled = models.BooleanField(default=False)

    class Meta:
        ordering = ['-registered_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_cancelled']),
            models.Index(fields=['event', 'is_cancelled']),
        ]
        # Prevent duplicate active registrations per email per event
        constraints = [
            models.UniqueConstraint(
                fields=['event', 'email'],
                condition=models.Q(is_cancelled=False),
                name='unique_active_registration_per_email_event'
            )
        ]

    def __str__(self):
        status = "cancelled" if self.is_cancelled else "active"
        return f"{self.name} → {self.event.title} [{status}]"
