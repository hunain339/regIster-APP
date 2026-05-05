"""
DRF serializers for Event and Registration models.
"""
from rest_framework import serializers
from django.utils import timezone
from .models import Event, Registration


class EventListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer used for paginated event listings.
    Includes computed fields for capacity status.
    """
    spots_remaining = serializers.IntegerField(read_only=True)
    total_registrations = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    is_past = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'date', 'location',
            'capacity', 'created_at', 'spots_remaining',
            'total_registrations', 'is_full', 'is_past',
        ]

    def get_is_past(self, obj):
        return obj.date < timezone.now()


class EventDetailSerializer(EventListSerializer):
    """
    Full event detail including nested active registrations count.
    Extends the list serializer with no additional DB fields needed
    (spots_remaining and is_full are already computed properties).
    """
    class Meta(EventListSerializer.Meta):
        fields = EventListSerializer.Meta.fields  # same fields, extendable


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and reading registrations.
    Performs capacity check and duplicate detection on creation.
    """
    event_title = serializers.CharField(source='event.title', read_only=True)
    event_date = serializers.DateTimeField(source='event.date', read_only=True)
    event_location = serializers.CharField(source='event.location', read_only=True)

    class Meta:
        model = Registration
        fields = [
            'id', 'event', 'event_title', 'event_date', 'event_location',
            'name', 'email', 'phone', 'registered_at', 'is_cancelled',
        ]
        read_only_fields = ['registered_at', 'is_cancelled']

    def validate_email(self, value):
        """Normalise email to lowercase."""
        return value.strip().lower()

    def validate(self, attrs):
        """
        Check:
        1. Event is not full.
        2. No active registration already exists for this email + event.
        """
        event = attrs.get('event')
        email = attrs.get('email', '').strip().lower()

        if event and event.is_full:
            raise serializers.ValidationError(
                {'event': 'This event has reached its maximum capacity.'}
            )

        if event and email:
            duplicate = Registration.objects.filter(
                event=event,
                email=email,
                is_cancelled=False
            ).exists()
            if duplicate:
                raise serializers.ValidationError(
                    {'email': 'An active registration already exists for this email and event.'}
                )

        return attrs

    def create(self, validated_data):
        # Attach authenticated user if available
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().create(validated_data)


class RegistrationCancelSerializer(serializers.ModelSerializer):
    """Minimal serializer used when cancelling a registration."""
    class Meta:
        model = Registration
        fields = ['id', 'is_cancelled']
