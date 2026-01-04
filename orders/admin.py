from django.contrib import admin
from .models import Order, OrderItem, Coupon
from django.utils.formats import date_format


class OrderItemInline(admin.TabularInline):
    """Встроенное отображение позиций заказа"""
    model = OrderItem
    extra = 0
    readonly_fields = ['dish', 'quantity', 'price_at_order']
    fields = ['dish', 'quantity', 'price_at_order']

    def total_price(self, obj):
        return obj.total_price

    total_price.short_description = 'Total Cost'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Админка для заказов"""
    list_display = [
        'id_short',
        'customer_name',
        'phone_number',
        'status',
        'total_cost',
        'final_cost',
        'created_at'
    ]
    list_filter = ['status', 'delivery_method', 'payment_method', 'created_at']
    search_fields = ['customer_name', 'phone_number', 'delivery_address', 'id']
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'customer_name',
        'phone_number',
        'total_cost',
        'discount',
        'coupon_code',
        'delivery_cost',
        'final_cost',
    ]
    inlines = [OrderItemInline]
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'id',
                'status',
                'created_at',
                'updated_at'
            )
        }),
        ('Данные покупателя', {
            'fields': (
                'customer_name',
                'phone_number',
                'delivery_address',
                'delivery_method',
                'payment_method'
            )
        }),
        ('Финансовая информация', {
            'fields': (
                'total_cost',
                'discount',
                'coupon_code',
                'delivery_cost',
                'final_cost',
            )
        }),
        ('Подтверждение', {
            'fields': (
                'is_confirmed',
                'sms_code_sent_at'
            ),
            'classes': ('collapse',)
        }),
    )

    def id_short(self, obj):
        return f"#{obj.id.hex[:8]}"

    id_short.short_description = 'Order ID'

    def save_model(self, request, obj, form, change):
        # Пересчитываем стоимость доставки при сохранении в админке
        obj.delivery_cost = obj.calculate_delivery_cost()
        super().save_model(request, obj, form, change)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """Админка для купонов"""
    list_display = ['code', 'discount_percent', 'discount_amount', 'is_active', 'valid_until', 'times_used']
    list_filter = ['is_active', 'valid_from', 'valid_until']
    search_fields = ['code']
    readonly_fields = ['times_used']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Админка для позиций заказа (отдельно)"""
    list_display = ['order', 'dish', 'quantity', 'price_at_order', 'total_price']
    list_filter = ['order__status']
    search_fields = ['order__id', 'dish__name']

    def total_price(self, obj):
        return obj.total_price

    total_price.short_description = 'Total Cost'
