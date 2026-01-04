from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 звезда'),
        (2, '2 звезды'),
        (3, '3 звезды'),
        (4, '4 звезды'),
        (5, '5 звезд'),
    ]

    author = models.CharField(max_length=100, verbose_name='Автор')
    text = models.TextField(verbose_name='Текст отзыва')
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Рейтинг'
    )
    image = models.ImageField(
        upload_to='reviews_images/',
        default='reviews_images/default.png',
        verbose_name='Фото автора'
    )
    admin_notified = models.BooleanField(
        default=False,
        verbose_name='Администратор уведомлен'
    )
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв от {self.author} ({self.rating} звезд)"

    def get_stars(self):
        """Возвращает HTML для отображения звезд рейтинга"""
        full_stars = self.rating
        empty_stars = 5 - full_stars
        stars_html = ''

        # Полные звезды
        for i in range(full_stars):
            stars_html += '<i class="fa fa-star"></i>'

        # Пустые звезды
        for i in range(empty_stars):
            stars_html += '<i class="fa fa-star-o"></i>'

        return stars_html
