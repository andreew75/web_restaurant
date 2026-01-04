# notifications/email.py

import logging
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_admin_email(subject: str, message: str) -> None:
    """
    Отправка email администратору
    """

    admin_email = getattr(settings, 'ADMIN_EMAIL', None)

    if not admin_email:
        logger.warning('ADMIN_EMAIL is not configured')
        return

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f'Email notification error: {e}')
