"""
Admin panel configuration for Event and Registration models.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Event, Registration


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """
    Full-featured admin for Event model.
    Shows capacity usage inline.
    """
    list_display = [
        'title', 'date', 'location',
        'capacity', 'registrations_count', 'spots_remaining_display', 'created_at',
    ]
    list_filter = ['date', 'location']
    search_fields = ['title', 'description', 'location']
    ordering = ['date']
    readonly_fields = ['created_at', 'spots_remaining_display', 'registrations_count']
    date_hierarchy = 'date'

    fieldsets = (
        ('Event Information', {
            'fields': ('title', 'description', 'date', 'location', 'capacity')
        }),
        ('Metadata', {
            'fields': ('created_at', 'registrations_count', 'spots_remaining_display'),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        """Optimise with prefetch to avoid N+1 on registration counts."""
        return super().get_queryset(request).prefetch_related('registrations')

    def registrations_count(self, obj):
        return obj.registrations.filter(is_cancelled=False).count()
    registrations_count.short_description = 'Registered'

    def spots_remaining_display(self, obj):
        remaining = obj.spots_remaining
        if remaining == 0:
            return format_html('<span style="color:red;font-weight:bold;">FULL</span>')
        elif remaining <= 5:
            return format_html(
                '<span style="color:orange;font-weight:bold;">{} left</span>', remaining
            )
        return format_html('<span style="color:green;">{} left</span>', remaining)
    spots_remaining_display.short_description = 'Spots Left'


class RegistrationInline(admin.TabularInline):
    """Inline view of registrations inside the Event admin."""
    model = Registration
    extra = 0
    readonly_fields = ['name', 'email', 'phone', 'registered_at', 'is_cancelled']
    can_delete = False
    show_change_link = True
    fields = ['name', 'email', 'phone', 'registered_at', 'is_cancelled']


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    """
    Admin for Registration model.
    Supports bulk cancellation via action.
    """
    list_display = [
        'name', 'email', 'phone', 'event_link',
        'registered_at', 'status_display',
    ]
    list_filter = ['is_cancelled', 'event', 'registered_at']
    search_fields = ['name', 'email', 'phone', 'event__title']
    ordering = ['-registered_at']
    readonly_fields = ['registered_at']
    raw_id_fields = ['event', 'user']
    actions = ['cancel_registrations', 'restore_registrations']

    def get_queryset(self, request):
        """Optimise with select_related to avoid N+1 on event data."""
        return super().get_queryset(request).select_related('event', 'user')

    def event_link(self, obj):
        return format_html(
            '<a href="/admin/events/event/{}/change/">{}</a>',
            obj.event_id, obj.event.title
        )
    event_link.short_description = 'Event'

    def status_display(self, obj):
        if obj.is_cancelled:
            return format_html('<span style="color:red;">Cancelled</span>')
        return format_html('<span style="color:green;">Active</span>')
    status_display.short_description = 'Status'

    @admin.action(description='Cancel selected registrations')
    def cancel_registrations(self, request, queryset):
        updated = queryset.filter(is_cancelled=False).update(is_cancelled=True)
        self.message_user(request, f'{updated} registration(s) cancelled.')

    @admin.action(description='Restore selected registrations')
    def restore_registrations(self, request, queryset):
        updated = queryset.filter(is_cancelled=True).update(is_cancelled=False)
        self.message_user(request, f'{updated} registration(s) restored.')
