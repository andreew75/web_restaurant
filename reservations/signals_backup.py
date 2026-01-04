import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from .models import Reservation

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Reservation)
def send_reservation_emails(sender, instance, created, **kwargs):
    """Отправляет email администраторам и клиенту при создании новой брони"""

    logger.info(f"=== EMAIL СИГНАЛ ЗАПУЩЕН ===")
    logger.info(f"Бронь #{instance.id}, created={created}")

    # Отправляем email только при создании новой записи и если email клиенту еще не отправлялся
    if created and not instance.email_sent:
        try:
            # 1. ОТПРАВКА EMAIL КЛИЕНТУ
            if instance.email:
                client_subject = f'Заявка на бронирование #{instance.id} принята'

                # Текстовая версия письма для клиента
                client_plain_message = f"""
Уважаемый(ая) {instance.name}!

Мы получили вашу заявку на бронирование столика в нашем ресторане!

Детали вашей заявки:
• Номер брони: #{instance.id}
• Дата визита: {instance.visit_date}
• Время: {instance.visit_time}
• Количество гостей: {instance.get_guests_display()}
• Телефон: {instance.phone}

В ближайшее время с вами свяжется администратор для подтверждения брони.

Если у вас есть вопросы, вы можете связаться с нами по телефону или ответить на это письмо.

С уважением,
Команда ресторана

---
Это автоматическое уведомление. Пожалуйста, не отвечайте на это письмо.
                """

                # Пытаемся отправить HTML версию, если шаблон существует
                try:
                    client_html_message = render_to_string('emails/reservation_client.html', {
                        'reservation': instance,
                        'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
                    })
                except:
                    # Если шаблона нет, используем только текстовую версию
                    client_html_message = None

                logger.info(f"Отправка email клиенту: {instance.email}")

                # Отправляем email клиенту
                send_mail(
                    subject=client_subject,
                    message=client_plain_message.strip(),
                    html_message=client_html_message,  # HTML версия (может быть None)
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.email],
                    fail_silently=False,
                )

                logger.info(f"✅ Email клиенту отправлен")

            # 2. ОТПРАВКА EMAIL АДМИНИСТРАТОРАМ
            admin_users = User.objects.filter(is_staff=True, is_active=True)
            admin_emails = [admin.email for admin in admin_users if admin.email]

            if admin_emails:
                admin_subject = f'✅ Новая бронь #{instance.id} от {instance.name}'

                # Ссылка на админку
                site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
                admin_link = f'{site_url}/admin/reservations/reservation/{instance.id}/change/'

                admin_message = f"""
📋 НОВОЕ БРОНИРОВАНИЕ #{instance.id}

👤 КЛИЕНТ
Имя: {instance.name}
Email: {instance.email}
Телефон: {instance.phone}

📅 БРОНИРОВАНИЕ
Гостей: {instance.get_guests_display()}
Дата: {instance.visit_date}
Время: {instance.visit_time}

💭 ДОПОЛНИТЕЛЬНО
Пожелания: {instance.special_request or "нет"}
Дата создания: {instance.created_at.strftime("%d.%m.%Y %H:%M")}

🔗 ССЫЛКА ДЛЯ ОБРАБОТКИ
{admin_link}

---
Это автоматическое уведомление от системы бронирования.
                """

                logger.info(f"Отправка email администраторам: {admin_emails}")

                send_mail(
                    subject=admin_subject,
                    message=admin_message.strip(),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=admin_emails,
                    fail_silently=False,
                )

                logger.info(f"✅ Email администраторам отправлен")

            # 3. ОБНОВЛЯЕМ ФЛАГИ ОТПРАВКИ В БАЗЕ ДАННЫХ
            instance.email_sent = True
            instance.admin_notified = True
            instance.is_processed = True

            # Сохраняем изменения, обходя повторный вызов сигнала
            Reservation.objects.filter(id=instance.id).update(
                email_sent=True,
                admin_notified=True,
                is_processed=True
            )

            logger.info(f"✅ Все email успешно отправлены для брони #{instance.id}")

        except Exception as e:
            logger.error(f"❌ Ошибка отправки email: {e}", exc_info=True)