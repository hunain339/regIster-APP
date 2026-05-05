"""
Email utilities for the events application.

Sends HTML + plain-text confirmation and cancellation emails using
Django's built-in email backend. Swap EMAIL_BACKEND in settings to
switch from console output to real SMTP in production.
"""
import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def _build_site_url(request=None):
    """
    Return the base site URL. Uses the request object when available,
    falls back to SITE_URL setting or a sensible default.
    """
    if request is not None:
        return request.build_absolute_uri('/').rstrip('/')
    return getattr(settings, 'SITE_URL', 'http://localhost:8000')


def send_registration_confirmation(registration, request=None):
    """
    Send a registration confirmation email to the attendee.

    Called immediately after a Registration row is created.

    Args:
        registration: Registration model instance (with event pre-loaded).
        request: Optional Django HttpRequest — used to build absolute URLs.
    """
    site_url = _build_site_url(request)

    context = {
        'registration': registration,
        'event': registration.event,
        'site_url': site_url,
        'event_url': f"{site_url}/events/{registration.event.pk}/",
        'my_registrations_url': f"{site_url}/events/my-registrations/",
        'year': timezone.now().year,
    }

    subject = f"You're registered! — {registration.event.title}"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [registration.email]

    # Plain-text fallback
    text_body = render_to_string('emails/registration_confirmation.txt', context)
    # Rich HTML body
    html_body = render_to_string('emails/registration_confirmation.html', context)

    msg = EmailMultiAlternatives(subject, text_body, from_email, to_email)
    msg.attach_alternative(html_body, 'text/html')

    try:
        msg.send()
        logger.info(
            "Confirmation email sent to %s for event '%s' (reg #%s)",
            registration.email, registration.event.title, registration.pk
        )
    except Exception as exc:
        # Never let an email failure break the registration flow
        logger.error(
            "Failed to send confirmation email to %s for reg #%s: %s",
            registration.email, registration.pk, exc
        )


def send_cancellation_notice(registration, request=None):
    """
    Send a cancellation notice email to the attendee.

    Called immediately after is_cancelled is set to True.

    Args:
        registration: Registration model instance (with event pre-loaded).
        request: Optional Django HttpRequest — used to build absolute URLs.
    """
    site_url = _build_site_url(request)

    context = {
        'registration': registration,
        'event': registration.event,
        'site_url': site_url,
        'event_url': f"{site_url}/events/{registration.event.pk}/",
        'browse_url': f"{site_url}/events/",
        'year': timezone.now().year,
    }

    subject = f"Registration Cancelled — {registration.event.title}"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [registration.email]

    text_body = render_to_string('emails/registration_cancellation.txt', context)
    html_body = render_to_string('emails/registration_cancellation.html', context)

    msg = EmailMultiAlternatives(subject, text_body, from_email, to_email)
    msg.attach_alternative(html_body, 'text/html')

    try:
        msg.send()
        logger.info(
            "Cancellation email sent to %s for event '%s' (reg #%s)",
            registration.email, registration.event.title, registration.pk
        )
    except Exception as exc:
        logger.error(
            "Failed to send cancellation email to %s for reg #%s: %s",
            registration.email, registration.pk, exc
        )
