from django.shortcuts import render, redirect
from menu.models import Category, MenuItem
from reviews.models import Review
from chefs.models import Chef
from django.contrib import messages
from reviews.forms import ReviewForm
from django.core.paginator import Paginator


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
    reviews = Review.objects.filter(is_published=True)[:6]
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


def reviews_page(request):
    """Страница с формой отправки отзыва и списком отзывов"""

    # Форма для отправки нового отзыва
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            # Сохраняем отзыв, но не публикуем сразу
            review = form.save(commit=False)
            review.is_published = False  # Требует модерации
            review.save()

            # messages.success(request, 'Спасибо за ваш отзыв! Он будет опубликован после проверки.')
            return render(request, 'reviews.html', {
                'form': ReviewForm(),
                'success': True,
                'show_modal': True,
            })
    else:
        form = ReviewForm()

    # # Получаем опубликованные отзывы для отображения
    # published_reviews = Review.objects.filter(is_published=True).order_by('-created_at')
    #
    # # Пагинация (например, по 5 отзывов на странице)
    # paginator = Paginator(published_reviews, 5)
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)

    context = {
        'form': form,
        'success': False,
        'show_modal': False,

        # 'page_obj': page_obj,
        # 'reviews': page_obj.object_list,
    }

    return render(request, 'reviews.html', context)
