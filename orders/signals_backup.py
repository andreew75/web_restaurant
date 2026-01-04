from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
from .models import Order, OrderItem
import logging
from .notifications_backup import send_admin_notifications, send_status_change_notification
# from .notifications import send_customer_confirmation

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def order_created_handler(sender, instance, created, **kwargs):
    """
    Обработчик создания нового заказа
    """
    if created:
        logger.info(f'New order created: #{instance.id.hex[:8]}')

        # Отправляем уведомления
        send_admin_notifications(instance)

        # Можно также отправлять SMS клиенту
        # if instance.is_confirmed:
        #     send_customer_confirmation(instance)


@receiver(post_save, sender=Order)
def order_status_changed_handler(sender, instance, **kwargs):
    """
    Обработчик изменения статуса заказа
    """
    # Проверяем, изменился ли статус
    if instance.tracker.has_changed('status'):
        old_status = instance.tracker.previous('status')
        new_status = instance.status

        logger.info(f'Order #{instance.id.hex[:8]} status changed: {old_status} -> {new_status}')

        # Отправляем уведомление об изменении статуса
        send_status_change_notification(instance, old_status, new_status)
