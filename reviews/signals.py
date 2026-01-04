import threading
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Review


def notify_admin_async(review_id):
    from notifications.telegram import send_telegram_message
    from notifications.email import send_admin_email
    from .models import Review

    try:
        review = Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        return

    message_text = (
        f'⭐ Новый отзыв (на модерации)\n'
        f'👤 Автор: {review.author}\n'
        f'⭐ Рейтинг: {review.get_rating_display()}\n\n'
        f'💬 Текст отзыва:\n{review.text}'
    )

    # ---- EMAIL ----
    send_admin_email(
        subject='Новый отзыв посетителя',
        message=message_text
    )

    # ---- TELEGRAM ----
    send_telegram_message(message_text)

    # помечаем, что администратор уведомлён
    review.admin_notified = True
    review.save(update_fields=['admin_notified'])


@receiver(post_save, sender=Review)
def review_created_notify(sender, instance: Review, created, **kwargs):
    if not created:
        return

    if instance.admin_notified:
        return

    threading.Thread(
        target=notify_admin_async,
        args=(instance.id,),
        daemon=True
    ).start()
