from django.shortcuts import render
from .models import MenuItem, Category


def menu_list(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'menu/list.html', context)


def dish_category(request):

    # Получаем все категории
    categories = Category.objects.prefetch_related('menuitem_set').all()

    breakfast_items = MenuItem.objects.filter(
        meal_types__code='breakfast',
        stop_list=False
    ).select_related('category').prefetch_related('meal_types').distinct()

    context = {
        'categories': categories,
        'breakfast_items': breakfast_items,
    }
    return render(request, 'menu/list.html', context)
