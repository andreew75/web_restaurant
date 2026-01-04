
import logging
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import requests
import json

logger = logging.getLogger(__name__)


class NotificationService:
    """Сервис для отправки уведомлений администраторам"""

    def __init__(self):
        self.telegram_bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        self.telegram_chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
        self.admin_email = getattr(settings, 'ADMIN_EMAIL', None)
        self.admin_phone = getattr(settings, 'ADMIN_PHONE', None)

        # Убираем импорт SMS сервиса из __init__ для избежания циклических импортов
        self._sms_service = None

    @property
    def sms_service(self):
        """Ленивая загрузка SMS сервиса (импортируем только когда нужно)"""
        if self._sms_service is None:
            # Импортируем здесь, а не в __init__
            from .sms_service_backup import sms_service
            self._sms_service = sms_service
        return self._sms_service

    def send_new_order_notification(self, order):
        """Отправка уведомления о новом заказе всеми способами"""
        order_info = self._format_order_info(order)

        # 1. Telegram (самый быстрый и удобный)
        if self.telegram_bot_token and self.telegram_chat_id:
            self._send_telegram_notification(order, order_info)

        # 2. Email (для истории и деталей)
        if self.admin_email:
            self._send_email_notification(order, order_info)

        # 3. SMS (если админ не онлайн)
        if self.admin_phone and getattr(settings, 'SEND_SMS_TO_ADMIN', False):
            self._send_sms_notification(order, order_info)

        # 4. Логирование
        logger.info(f'New order notification sent: #{order.id.hex[:8]}')

    def send_status_change_notification(self, order, old_status, new_status):
        """Уведомление об изменении статуса заказа"""
        if self.telegram_bot_token and self.telegram_chat_id:
            message = (
                f"🔄 Статус заказа изменен\n"
                f"Заказ: #{order.id.hex[:8]}\n"
                f"Клиент: {order.customer_name}\n"
                f"Статус: {order.get_status_display()} ({old_status} → {new_status})\n"
                f"Сумма: {order.final_cost} ₽"
            )
            self._send_telegram_message(message)

    def _format_order_info(self, order):
        """Форматирование информации о заказе"""
        items_text = "\n".join([
            f"  • {item.dish_name} x{item.quantity} = {item.total_price} ₽"
            for item in order.items.all()
        ])

        return {
            'id_short': order.id.hex[:8].upper(),
            'customer_name': order.customer_name,
            'phone': order.phone_number,
            'address': order.delivery_address or "Самовывоз",
            'delivery_method': order.get_delivery_method_display(),
            'payment_method': order.get_payment_method_display(),
            'items_count': order.items.count(),
            'total_cost': order.total_cost,
            'discount': order.discount,
            'delivery_cost': order.delivery_cost,
            'final_cost': order.final_cost,
            'items_text': items_text,
            'coupon': order.coupon_code or "нет",
            'status': order.get_status_display(),
            'created_at': order.created_at.strftime('%d.%m.%Y %H:%M'),
        }

    def _send_telegram_notification(self, order, order_info):
        """Отправка уведомления в Telegram"""
        try:
            message = (
                f"🆕 НОВЫЙ ЗАКАЗ!\n"
                f"Номер: #{order_info['id_short']}\n"
                f"Время: {order_info['created_at']}\n"
                f"Клиент: {order_info['customer_name']}\n"
                f"Телефон: {order_info['phone']}\n"
                f"Адрес: {order_info['address']}\n"
                f"Доставка: {order_info['delivery_method']}\n"
                f"Оплата: {order_info['payment_method']}\n"
                f"Товары ({order_info['items_count']}):\n"
                f"{order_info['items_text']}\n"
                f"Итого: {order_info['final_cost']} ₽\n"
                f"Купон: {order_info['coupon']}\n"
                f"Статус: {order_info['status']}\n"
                f"\n"
                f"Ссылка в админку: {settings.SITE_URL}/admin/orders/order/{order.id}/"
            )

            self._send_telegram_message(message)

        except Exception as e:
            logger.error(f"Telegram notification error: {str(e)}")

    def _send_telegram_message(self, message):
        """Отправка сообщения в Telegram"""
        if not self.telegram_bot_token or not self.telegram_chat_id:
            logger.warning("Telegram credentials not configured")
            return

        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"

        payload = {
            'chat_id': self.telegram_chat_id,
            'text': message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True,
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Telegram message sent successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {str(e)}")
            return False

    def _send_email_notification(self, order, order_info):
        """Отправка уведомления по email"""
        try:
            if not self.admin_email:
                logger.warning("Admin email not configured")
                return

            subject = f"Новый заказ #{order_info['id_short']} - {settings.SITE_NAME}"

            # Список возможных путей к шаблону (в порядке приоритета)
            possible_templates = [
                'emails/new_order.html',  # Глобальный шаблон
                'emails/new_order_admin.html',  # Альтернативное имя
                'orders/emails/new_order.html',  # Шаблон в приложении
                'orders/emails/new_order_admin.html',
            ]

            html_message = None

            # Ищем существующий шаблон
            for template_name in possible_templates:
                try:
                    html_message = render_to_string(template_name, {
                        'order': order,
                        'order_info': order_info,
                        'site_name': settings.SITE_NAME,
                        'site_url': settings.SITE_URL,
                    })
                    logger.debug(f"Using email template: {template_name}")
                    break
                except Exception:
                    continue

            # Если шаблон не найден, создаем простой HTML
            if not html_message:
                logger.warning("Email template not found, using fallback")
                html_message = self._create_fallback_email_html(order_info)

            # Текстовая версия
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.admin_email],
                fail_silently=False,
            )

            logger.info(f"Email notification sent to {self.admin_email}")
            return True

        except Exception as e:
            logger.error(f"Email notification error: {str(e)}")
            return False

    def _create_fallback_email_html(self, order_info):
        """Создание простого HTML письма если шаблон не найден"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Новый заказ</title>
        </head>
        <body>
            <h1>Новый заказ #{order_info['id_short']}</h1>
            <p><strong>Дата:</strong> {order_info['created_at']}</p>
            <p><strong>Клиент:</strong> {order_info['customer_name']}</p>
            <p><strong>Телефон:</strong> {order_info['phone']}</p>
            <p><strong>Адрес:</strong> {order_info['address']}</p>
            <p><strong>Сумма:</strong> {order_info['final_cost']} ₽</p>
            <hr>
            <p>Перейдите в админку для просмотра деталей заказа.</p>
        </body>
        </html>
        """

    def _send_sms_notification(self, order, order_info):
        """Отправка SMS уведомления администратору"""
        try:
            if not self.admin_phone:
                logger.warning("Admin phone not configured")
                return False

            message = (
                f"Новый заказ #{order_info['id_short']}. "
                f"{order_info['customer_name']}, {order_info['final_cost']} ₽. "
                f"{settings.SITE_URL}/admin/"
            )

            # Используем property для ленивой загрузки
            result = self.sms_service.send_sms(self.admin_phone, message)

            if result.get('success'):
                logger.info(f"SMS notification sent to admin. Cost: {result.get('cost', 0)} RUB")
                return True
            else:
                logger.error(f"SMS notification failed: {result.get('error', 'Unknown error')}")
                return False

        except ImportError as e:
            logger.error(f"SMS service not available: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"SMS notification error: {str(e)}")
            return False


# Синглтон экземпляр
notification_service = NotificationService()


# Функции для использования в signals
def send_admin_notifications(order):
    """Отправка уведомлений администраторам"""
    notification_service.send_new_order_notification(order)


def send_status_change_notification(order, old_status, new_status):
    """Уведомление об изменении статуса"""
    notification_service.send_status_change_notification(order, old_status, new_status)


# def send_customer_confirmation(order):
#     """Отправка подтверждения клиенту"""
#     try:
#         from .sms_service import sms_service
#         sms_service.send_order_confirmation(order.phone_number, order.id.hex[:8])
#         return True
#     except ImportError as e:
#         logger.error(f"Cannot send SMS confirmation: {str(e)}")
#         return False
#     except Exception as e:
#         logger.error(f"Error sending SMS confirmation: {str(e)}")
#         return False
