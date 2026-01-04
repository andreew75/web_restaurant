import threading
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Reservation
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings


def notify_admin_async(reservation_id):
    from notifications.telegram import send_telegram_message
    from notifications.email import send_admin_email
    from .models import Reservation

    try:
        reservation = Reservation.objects.get(id=reservation_id)
    except Reservation.DoesNotExist:
        return


    message_text = (
        f'📅 Новое бронирование\n'
        f'👤 Имя: {reservation.name}\n'
        f'📞 Телефон: {reservation.phone}\n'
        f'✉️ Email: {reservation.email}\n'
        f'👥 Гостей: {reservation.guests}\n'
        f'🗓 Дата: {reservation.visit_date.strftime('%d.%m.%Y')}\n'
        f'⏰ Время: {reservation.visit_time.strftime('%H:%M')}\n'
    )

    if reservation.special_request:
        message_text += f'\n📝 Пожелания:\n{reservation.special_request}'

    # ---- EMAIL ----
    send_admin_email(
        subject='Новое бронирование столика',
        message=message_text
    )

    # ---- TELEGRAM ----
    send_telegram_message(message_text)

    # помечаем, что администратор уведомлён
    reservation.admin_notified = True
    reservation.save(update_fields=['admin_notified'])


@receiver(post_save, sender=Reservation)
def reservation_created_notify(sender, instance: Reservation, created, **kwargs):
    if not created:
        return

    if instance.admin_notified:
        return

    threading.Thread(
        target=notify_admin_async,
        args=(instance.id,),
        daemon=True
    ).start()


    # Отправка сообщения клиенту о подтверждении брони (async)
def send_client_confirmation_email_async(reservation_id):
    try:
        reservation = Reservation.objects.get(id=reservation_id)
    except Reservation.DoesNotExist:
        return

    subject = 'Подтверждение бронирования столика | Saffron'

    html_content = render_to_string(
        'emails/reservation_client.html',
        {'reservation': reservation}
    )

    email = EmailMultiAlternatives(
        subject=subject,
        body='Ваше бронирование подтверждено!',  # fallback для text-only
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[reservation.email],
    )
    email.attach_alternative(html_content, "text/html")

    try:
        email.send()
        reservation.email_sent = True
        reservation.save(update_fields=['email_sent'])
    except Exception:
        # если письмо не ушло — флаг не ставим
        pass


@receiver(post_save, sender=Reservation)
def reservation_confirmed_notify_client(sender, instance: Reservation, **kwargs):
    # Проверяем, что is_confirmed изменился
    if not instance.tracker.has_changed('is_confirmed'):
        return

    # Нужно строго False → True
    if (
        instance.tracker.previous('is_confirmed') is False
        and instance.is_confirmed is True
        and not instance.email_sent
    ):
        threading.Thread(
            target=send_client_confirmation_email_async,
            args=(instance.id,),
            daemon=True
        ).start()
