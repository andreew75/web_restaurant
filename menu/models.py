from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Name category')
    order = models.IntegerField(default=0, verbose_name='Order')
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['order']

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Завтрак'),
        ('lunch', 'Обед'),
        ('dinner', 'Ужин'),
        ('any', 'Любое время'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    ingredients = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)

    meal_types = models.ManyToManyField(
        'MealType',
        verbose_name='Тип блюда',
        blank=True
    )

    image = models.ImageField(upload_to='menu_images/', blank=True)
    image_dish = models.ImageField(upload_to='menu_images/', default='menu_images/default.png')
    calories = models.IntegerField(blank=True, null=True)
    is_special = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    cooking_time = models.IntegerField(default=15)
    stop_list = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Блюдо'
        verbose_name_plural = 'Блюда'
        ordering = ['category__order', 'name']

    def __str__(self):
        return f"{self.name} - {self.price}"


class MealType(models.Model):
    code = models.CharField(max_length=20, choices=MenuItem.MEAL_TYPE_CHOICES, unique=True)

    class Meta:
        verbose_name = 'Тип блюда'
        verbose_name_plural = 'Типы блюд'

    def __str__(self):
        return dict(MenuItem.MEAL_TYPE_CHOICES).get(self.code, self.code)

    def get_name(self):
        """Возвращает человеко-читаемое название"""
        return dict(MenuItem.MEAL_TYPE_CHOICES).get(self.code, self.code)
