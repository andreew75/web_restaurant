
from django.contrib import admin
from menu.models import MenuItem, Category, MealType


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_filter = ('category', 'stop_list', 'is_special', 'is_new', 'meal_types')
    list_display = ('name', 'category', 'price', 'stop_list', 'is_special', 'is_new')
    list_editable = ('stop_list', 'is_special', 'is_new')
    search_fields = ('name', 'description', 'ingredients')

    # Группировка полей в форме редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'category', 'price', 'description', 'ingredients')
        }),
        ('Изображения', {
            'fields': ('image', 'image_dish')
        }),
        ('Дополнительно', {
            'fields': ('meal_types', 'calories', 'cooking_time',
                       'is_special', 'is_new', 'stop_list')
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'item_count')
    list_editable = ('order',)  # Можно менять порядок прямо в списке

    def item_count(self, obj):
        return obj.menuitem_set.count()

    item_count.short_description = 'Количество блюд'


@admin.register(MealType)
class MealTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'get_name', 'item_count')

    def get_name(self, obj):
        return obj.get_name()

    get_name.short_description = 'Название'

    def item_count(self, obj):
        return obj.menuitem_set.count()

    item_count.short_description = 'Блюд'

