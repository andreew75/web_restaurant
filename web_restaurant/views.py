from django.shortcuts import render
from menu.models import Category, MenuItem
from reviews.models import Review
from chefs.models import Chef


def home(request):
    # Для секции Specials - берем 6 блюд, помеченных как специальные
    special_dishes = MenuItem.objects.filter(is_special=True)[:6]
    # Для секции New Dishes - берем 2 блюда, помеченных как Новинки
    new_dishes = MenuItem.objects.filter(is_new=True)[:2]

    # Если специальных блюд меньше 6, дополняем обычными
    if len(special_dishes) < 6:
        additional_dishes = MenuItem.objects.exclude(is_special=True)[:6 - len(special_dishes)]
        special_dishes = list(special_dishes) + list(additional_dishes)
        new_dishes = list(new_dishes) + list(additional_dishes)

    # Для секции Menu9 - берем по одному блюду из каждой категории
    menu_categories = Category.objects.all()[:6]
    category_dishes = []
    for category in menu_categories:
        dish = MenuItem.objects.filter(category=category).first()
        if dish:
            category_dishes.append({
                'category': category,
                'dish': dish
            })
        # Для каждой категории получаем 6 блюд
        category.menu_items = MenuItem.objects.filter(category=category)[:6]

        # Секция Testimonials - отзывы клиентов
    reviews = Review.objects.filter(is_published=True)[:3]
    # Секция Shes - команда
    chefs = Chef.objects.filter(is_active=True).order_by('order')[:4]

    context = {
        'special_dishes': special_dishes,
        'new_dishes': new_dishes,
        'menu_categories': menu_categories,
        'category_dishes': category_dishes,
        'reviews': reviews,
        'chefs': chefs,
    }

    return render(request, 'home.html', context)


def reviews(request):
    return render(request, 'reviews.html')
