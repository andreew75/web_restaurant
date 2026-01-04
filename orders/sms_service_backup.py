import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class SMSService:
    """Базовый сервис для отправки SMS (заглушка)"""

    def __init__(self):
        self.api_key = getattr(settings, 'SMS_API_KEY', '')
        self.sender = getattr(settings, 'SMS_SENDER', 'REST')
        self.test_mode = getattr(settings, 'SMS_TEST_MODE', True)

    def send_sms(self, phone, message):
        """Отправка SMS (заглушка для тестирования)"""
        if self.test_mode:
            logger.info(f"[TEST SMS] To: {phone}, Message: {message[:50]}...")
            return {
                'success': True,
                'message_id': 'test_mode',
                'cost': 0,
                'balance': 100
            }

        logger.warning("SMS service not configured. Running in test mode.")
        return {
            'success': False,
            'error': 'SMS service not configured',
            'cost': 0,
            'balance': 0
        }

    def send_order_confirmation(self, phone, order_number):
        """Отправка подтверждения заказа клиенту"""
        message = (
            f"Спасибо за заказ в {getattr(settings, 'SITE_NAME', 'Ресторан')}! "
            f"Ваш заказ №{order_number} принят. "
            f"Свяжемся с вами для подтверждения."
        )
        return self.send_sms(phone, message)

    def get_balance(self):
        """Получение баланса"""
        return {
            'success': True,
            'balance': 100.0,
            'currency': 'RUB',
        }


# Синглтон экземпляр
sms_service = SMSService()