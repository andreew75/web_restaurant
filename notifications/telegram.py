import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_telegram_message(text: str) -> None:
    """
    Отправка сообщения администратору в Telegram
    """

    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)

    if not token or not chat_id:
        logger.warning('Telegram settings are not configured')
        return

    url = f'https://api.telegram.org/bot{token}/sendMessage'

    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True,
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
    except Exception as e:
        logger.error(f'Telegram notification error: {e}')
