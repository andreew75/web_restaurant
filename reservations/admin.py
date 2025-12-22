from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'guests', 'visit_date', 'visit_time', 'is_confirmed', 'is_processed', 'email_sent', 'admin_notified', 'created_at']
    list_filter = ['email_sent', 'admin_notified', 'is_confirmed', 'is_processed', 'visit_date']
    search_fields = ['name', 'email', 'phone']
    list_editable = ['is_confirmed', 'is_processed']
    readonly_fields = ['created_at', 'email_sent', 'admin_notified']

    fieldsets = (
        ('Информация о клиенте', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Детали бронирования', {
            'fields': ('guests', 'visit_date', 'visit_time', 'special_request')
        }),
        ('Статус отправки email', {
            'fields': ('email_sent', 'admin_notified', 'created_at')
        }),
        ('Статус брони', {
            'fields': ('is_confirmed', 'is_processed')
        }),
    )
