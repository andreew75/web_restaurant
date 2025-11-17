from django.db import models


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Name category')
    order = models.IntegerField(default=0, verbose_name='Order')

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['order']

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    MEAL_TYPES_CHOICES = [
        ('breakfast', 'Завтрак'),
        ('lunch', 'Обед'),
        ('dinner', 'Ужин'),
        ('any', 'Любое время'),
    ]

    name = models.CharField(max_length=200, verbose_name='Name item')
    description = models.TextField(verbose_name='Description item')
    ingredients = models.TextField(verbose_name='Ingredients')
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Price')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Category')
    meal_type = models.CharField(choices=MEAL_TYPES_CHOICES, max_length=30, default='any', verbose_name='Type')
    image = models.ImageField(upload_to='menu_images/', verbose_name='Image')
    calories = models.IntegerField(verbose_name='Calories', blank=True, null=True)
    is_special = models.BooleanField(default=False, verbose_name='Special')
    is_new = models.BooleanField(default=False, verbose_name='New')
    cooking_time = models.IntegerField(default=15, verbose_name='Cooking time', blank=True, null=True)

    class Meta:
        verbose_name = "Menu item"
        verbose_name_plural = "Menu items"
        ordering = ['category__order', 'name']

    def __str__(self):
        return self.name

