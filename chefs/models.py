from django.db import models


class Chef(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя')
    position = models.CharField(max_length=100, verbose_name='Должность')
    bio = models.TextField(verbose_name='Биография')
    image = models.ImageField(upload_to='chefs_images/', verbose_name='Фото')
    experience = models.IntegerField(verbose_name='Опыт работы (лет)')
    specialty = models.CharField(max_length=100, verbose_name='Специализация')
    is_active = models.BooleanField(default=True, verbose_name='Активный сотрудник')
    order = models.IntegerField(default=0, verbose_name='Порядок отображения')

    class Meta:
        verbose_name = 'Шеф-повар'
        verbose_name_plural = 'Шеф-повара'
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} - {self.position}"
