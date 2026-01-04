from django.db import models
from django.utils import timezone
from model_utils import FieldTracker


class Reservation(models.Model):
    GUESTS_CHOICES = [
        (1, '1 People'),
        (2, '2 People'),
        (3, '3 People'),
        (4, '4 People'),
        (5, '5 People'),
        (6, '6 People'),
        (8, 'more than 6 People'),
    ]

    name = models.CharField(max_length=100, verbose_name='Имя')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    guests = models.IntegerField(choices=GUESTS_CHOICES, verbose_name='Количество гостей')
    visit_date = models.DateField(verbose_name='Дата визита')
    visit_time = models.TimeField(verbose_name='Время визита')
    special_request = models.TextField(blank=True, verbose_name='Особые пожелания')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_confirmed = models.BooleanField(default=False, verbose_name='Подтверждено')
    is_processed = models.BooleanField(default=False, verbose_name='Обработано')
    email_sent = models.BooleanField(
        default=False,
        verbose_name='Email отправлен клиенту'
    )
    admin_notified = models.BooleanField(
        default=False,
        verbose_name='Администратор уведомлен'
    )

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.visit_date} {self.visit_time}'

    tracker = FieldTracker(fields=['is_confirmed'])
