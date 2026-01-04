from django.shortcuts import render, get_object_or_404, redirect
from .models import MenuItem, Category
from django.contrib import messages
from orders.cart import Cart


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

    drinks_items = MenuItem.objects.filter(
        category__name='drinks',
        stop_list=False
    ).select_related('category').prefetch_related('meal_types').distinct()

    desserts_items = MenuItem.objects.filter(
        category__name='desserts',
        stop_list=False
    ).select_related('category').prefetch_related('meal_types').distinct()

    context = {
        'categories': categories,
        'breakfast_items': breakfast_items,
        'drinks_items': drinks_items,
        'desserts_items': desserts_items,
    }
    return render(request, 'menu/list.html', context)


def add_to_cart(request, dish_id):

    from .models import MenuItem

    dish = get_object_or_404(MenuItem, id=dish_id)

    # Проверяем, доступно ли блюдо для доставки
    if not dish.is_delivery:
        messages.error(request, f'Блюдо "{dish.name}" временно недоступно для доставки.')
        return redirect('menu:menu_list')  # Или другой URL вашего меню

    # Проверяем, не в стоп-листе ли блюдо
    if dish.stop_list:
        messages.warning(request, f'Блюдо "{dish.name}" временно отсутствует.')
        return redirect('menu:menu_list')

    # Получаем количество из GET-параметра (по умолчанию 1)
    quantity = int(request.GET.get('quantity', 1))

    # Добавляем блюдо в корзину
    cart = Cart(request)
    cart.add(dish, quantity)

    # Перенаправляем обратно на страницу, откуда пришел запрос
    scroll_to = request.GET.get('scroll_to', '')

    redirect_url = request.META.get('HTTP_REFERER', 'menu:menu_list')

    if scroll_to and '#' not in redirect_url:
        if '?' in redirect_url:
            redirect_url = f"{redirect_url}#{scroll_to}"
        else:
            redirect_url = f"{redirect_url}#{scroll_to}"

    return redirect(redirect_url)


def remove_from_cart(request, dish_id):
    """
    Удалить блюдо из корзины
    """
    from .models import MenuItem

    dish = get_object_or_404(MenuItem, id=dish_id)
    cart = Cart(request)
    cart.remove(dish)

    # messages.success(request, f'Блюдо "{dish.name}" удалено из корзины.')

    redirect_url = request.META.get('HTTP_REFERER', 'orders:cart_detail')
    return redirect(redirect_url)
