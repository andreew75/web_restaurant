from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
# from notifications.telegram import send_telegram_message
# from notifications.email import send_admin_email
import threading


def build_order_items_text(order):
    """
    Формирует текст состава заказа для Telegram
    """
    lines = []

    for item in order.items.all():
        lines.append(
            f'• {item.dish_name} ×{item.quantity} — {item.total_price}'
        )

    if not lines:
        return '— нет позиций —'

    return '\n'.join(lines)


def notify_admin_async(order_id):
    from notifications.telegram import send_telegram_message
    from notifications.email import send_admin_email
    from .models import Order

    try:
        order = Order.objects.prefetch_related('items').get(id=order_id)
    except Order.DoesNotExist:
        return

    items_text = build_order_items_text(order)

    message_text = (
        f'🧾 *Новый подтверждённый заказ*\n'
        f'ID: `{order.id.hex[:8]}`\n'
        f'👤 {order.customer_name}\n'
        f'📞 {order.phone_number}\n'
        f'💳 Оплата: {order.get_payment_method_display()}\n'
        f'🚚 Доставка: {order.delivery_cost}\n\n'
        f'🍽 Состав заказа:\n'
        f'{items_text}\n\n'
        f'💰 Сумма: {order.final_cost}\n'
    )

    # ---- EMAIL ----
    send_admin_email(
        subject='🧾 Новый подтверждённый заказ',
        message=message_text
    )

    # ---- TELEGRAM ----
    send_telegram_message(message_text)


@receiver(post_save, sender=Order)
def order_confirmed_notify(sender, instance, **kwargs):
    """
    Уведомляем админа ТОЛЬКО когда заказ подтверждён по SMS
    """
    if not instance.tracker.has_changed('is_confirmed'):
        return

    if instance.tracker.previous('is_confirmed') is False and instance.is_confirmed is True:
        threading.Thread(
            target=notify_admin_async,
            args=(instance.id,),
            daemon=True
        ).start()
