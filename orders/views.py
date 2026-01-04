from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .cart import Cart
from menu.models import MenuItem
from .models import Coupon, Order, OrderItem
import hashlib
import random
import django.utils.timezone as timezone


def cart_detail(request):
    cart = Cart(request)
    cart_items = list(cart)

    total_price = cart.get_total_price()

    # --- купон ---
    coupon_code = request.session.get('applied_coupon')
    discount = 0
    applied_coupon = None

    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_valid(order_amount=total_price):
                discount = coupon.calculate_discount(total_price)
                applied_coupon = coupon
            else:
                del request.session['applied_coupon']
        except Coupon.DoesNotExist:
            del request.session['applied_coupon']

    # ✅ subtotal после скидки
    cart_subtotal = max(total_price - discount, 0)

    # доставка считается от subtotal
    delivery_cost = cart.get_delivery_cost(cart_subtotal)

    # итог
    final_price = cart_subtotal + delivery_cost

    context = {
        'cart': cart,
        'cart_items': cart_items,

        'total_price': total_price,
        'discount': discount,
        'cart_subtotal': cart_subtotal,
        'delivery_cost': delivery_cost,
        'final_price': final_price,

        'applied_coupon': applied_coupon,

        'free_delivery_threshold': 100,
        'fixed_delivery_cost': 5,
    }

    return render(request, 'orders/cart_detail.html', context)


@require_POST
def cart_update(request):
    """
    Обновление количества товаров в корзине (AJAX/POST запрос)
    """
    cart = Cart(request)

    # Получаем данные из формы
    dish_id = request.POST.get('dish_id')
    quantity = request.POST.get('quantity')
    action = request.POST.get('action')

    response_data = {
        'success': False,
        'message': '',
        'item_removed': False,
        'item_total': 0,
        'cart_item_count': cart.get_item_count(),
        'cart_total': float(cart.get_total_price()),
    }

    if dish_id:
        if action == 'remove':
            # Удалить товар из корзины
            try:
                dish = MenuItem.objects.get(id=dish_id)
                cart.remove(dish)
                response_data.update({
                    'success': True,
                    'item_removed': True,
                    'cart_item_count': cart.get_item_count(),
                    'cart_total': float(cart.get_total_price())
                })
            except MenuItem.DoesNotExist:
                response_data['message'] = 'Item not found'

        elif quantity and quantity.isdigit():
            # Обновить количество
            quantity = int(quantity)
            if cart.update_quantity(dish_id, quantity):
                if quantity == 0:
                    # Если количество стало 0, удаляем товар
                    try:
                        dish = MenuItem.objects.get(id=dish_id)
                        cart.remove(dish)
                        response_data.update({
                            'success': True,
                            'item_removed': True,
                            'cart_item_count': cart.get_item_count(),
                            'cart_total': float(cart.get_total_price()),
                        })
                    except MenuItem.DoesNotExist:
                        response_data['message'] = 'Item not found'
                else:
                    # Получаем обновленную информацию о позиции
                    for item in cart.get_items_with_details():
                        if str(item['dish_id']) == str(dish_id):
                            response_data.update({
                                'success': True,
                                'quantity': item['quantity'],
                                'item_total': float(item['total_price']),  # Конвертируем Decimal в float для JSON
                                'item_removed': False,
                                'cart_item_count': cart.get_item_count(),
                                'cart_total': float(cart.get_total_price()),
                            })
                            break
            else:
                response_data['message'] = 'Item not found in cart'

    return JsonResponse(response_data)


@require_POST
def apply_coupon(request):
    """
    Применение купона
    """
    cart = Cart(request)
    coupon_code = request.POST.get('coupon_code', '').strip()

    if not coupon_code:
        messages.error(request, 'Please enter a coupon code')
        return redirect('orders:cart_detail')

    try:
        coupon = Coupon.objects.get(code=coupon_code)

        if coupon.is_valid(order_amount=cart.get_total_price()):
            request.session['applied_coupon'] = coupon_code
            return JsonResponse({
                'success': True
            })

        return JsonResponse({
            'success': False,
            'message': 'Coupon is not valid for this order'
        })

    except Coupon.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Invalid coupon code'
        })


@require_POST
def update_totals(request):
    cart = Cart(request)

    # Базовая сумма товаров
    subtotal = cart.get_total_price()

    # Купон
    discount = 0
    coupon_code = request.session.get('applied_coupon')

    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_valid(subtotal):
                discount = coupon.calculate_discount(subtotal)
        except Coupon.DoesNotExist:
            pass

    # Subtotal с учётом скидки
    cart_subtotal = max(subtotal - discount, 0)

    # Доставка считается от суммы ПОСЛЕ скидки
    delivery_cost = cart.get_delivery_cost(cart_subtotal)

    # Итог
    order_total = cart_subtotal + delivery_cost

    return JsonResponse({
        'success': True,
        'subtotal': float(subtotal),
        'discount': float(discount),
        'cart_subtotal': float(cart_subtotal),
        'delivery_cost': float(delivery_cost),
        'order_total': float(order_total),
        'free_delivery_threshold': 100,
        'fixed_delivery_cost': 5,
    })


def cart_clear(request):
    """
    Очистить корзину
    """
    cart = Cart(request)
    cart.clear()

    # Очищаем также примененный купон
    if 'applied_coupon' in request.session:
        del request.session['applied_coupon']

    messages.success(request, 'Cart cleared')
    return redirect('orders:cart_detail')


def cart_summary(request):
    """
    Получение сводной информации по корзине для AJAX-запросов
    """
    cart = Cart(request)

    # Получаем скидку
    coupon_code = request.session.get('applied_coupon')
    discount = 0
    # applied_coupon = None

    if coupon_code:
        try:
            applied_coupon = Coupon.objects.get(code=coupon_code)
            if applied_coupon.is_valid(order_amount=cart.get_total_price()):
                discount = applied_coupon.calculate_discount(cart.get_total_price())
        except Coupon.DoesNotExist:
            pass

    # Рассчитываем суммы
    total_price = cart.get_total_price()
    delivery_cost = cart.get_delivery_cost(total_price)
    final_price = cart.get_final_price(discount)

    return JsonResponse({
        'success': True,
        'total_price': float(total_price),
        'discount': float(discount),
        'delivery_cost': float(delivery_cost),
        'final_price': float(final_price),
        'free_delivery_threshold': 100,
        'fixed_delivery_cost': 5,
        'item_count': cart.get_item_count(),
        'unique_item_count': cart.get_unique_item_count(),
        'is_empty': cart.is_empty(),
    })


@require_POST
def checkout(request):
    """
    Создание заказа и отправка SMS кода
    """
    cart = Cart(request)

    if cart.is_empty():
        return JsonResponse({
            'success': False,
            'message': 'Your cart is empty'
        })

    # Проверяем согласие с условиями
    if not request.POST.get('agree'):
        return JsonResponse({
            'success': False,
            'message': 'Please agree to the Terms and Privacy Policy'
        })

    # Получаем данные из формы
    customer_name = request.POST.get('customer_name', '').strip()
    phone_number = request.POST.get('phone_number', '').strip()
    delivery_address = request.POST.get('delivery_address', '').strip()
    payment_method = request.POST.get('payment_method', 'cash')

    # Валидация данных
    errors = []

    if not customer_name:
        errors.append('Please enter your name')

    if not phone_number:
        errors.append('Please enter your phone number')

    if not delivery_address:
        errors.append('Please enter delivery address')

    if errors:
        return JsonResponse({
            'success': False,
            'message': ', '.join(errors)
        })

    # Рассчитываем суммы
    total_price = cart.get_total_price()

    # Применяем купон если есть
    coupon_code = request.session.get('applied_coupon')
    discount = 0
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_valid(order_amount=total_price):
                discount = coupon.calculate_discount(total_price)
                # Отмечаем купон как использованный
                coupon.mark_as_used()
        except Coupon.DoesNotExist:
            pass

    # Рассчитываем доставку
    delivery_cost = cart.get_delivery_cost(total_price - discount)

    try:
        # Создаем заказ
        order = Order.objects.create(
            customer_name=customer_name,
            phone_number=phone_number,
            delivery_address=delivery_address,
            payment_method=payment_method,
            total_cost=total_price,
            discount=discount,
            delivery_cost=delivery_cost,
            final_cost=total_price - discount + delivery_cost,
            coupon_code=coupon_code if coupon_code else None,
            status=Order.STATUS_NEW
        )

        # Добавляем товары в заказ
        for item in cart.get_items_with_details():
            OrderItem.objects.create(
                order=order,
                dish=item['dish'],
                quantity=item['quantity'],
                price_at_order=item['price'],
                dish_name=item['dish'].name
            )

        # Генерируем SMS код (4 цифры)
        sms_code = str(random.randint(1000, 9999))

        # Сохраняем хэш кода в заказе
        order.sms_code = hashlib.sha256(sms_code.encode()).hexdigest()
        order.sms_code_sent_at = timezone.now()
        order.save()

        # Отправляем SMS (заглушка - в реальности используйте SMS сервис)
        print(f"DEBUG: SMS code for order {order.id}: {sms_code}")
        # Здесь будет вызов функции отправки SMS

        # Сохраняем ID заказа в сессии для верификации
        request.session['pending_order_id'] = str(order.id)

        # Очищаем купон из сессии
        if 'applied_coupon' in request.session:
            del request.session['applied_coupon']

        return JsonResponse({
            'success': True,
            'message': 'SMS code sent to your phone',
            'order_id': str(order.id)
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating order: {str(e)}'
        })


@require_POST
def verify_sms(request):
    """
    Проверка SMS кода и подтверждение заказа
    """
    sms_code = request.POST.get('sms_code', '').strip()
    order_id = request.session.get('pending_order_id')

    if not sms_code or not order_id:
        return JsonResponse({
            'success': False,
            'message': 'Invalid code'
        })

    if not sms_code.isdigit() or len(sms_code) != 4:
        return JsonResponse({
            'success': False,
            'message': 'Please enter a valid 4-digit code'
        })

    try:
        order = Order.objects.get(id=order_id)

        # Проверяем код
        code_hash = hashlib.sha256(sms_code.encode()).hexdigest()

        if order.sms_code == code_hash:
            # Код верный - подтверждаем заказ
            order.is_confirmed = True
            order.status = Order.STATUS_CONFIRMED
            order.save()

            # Очищаем корзину и сессию
            cart = Cart(request)
            cart.clear()
            del request.session['pending_order_id']

            return JsonResponse({
                'success': True,
                'message': 'Order confirmed successfully!'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid SMS code'
            })

    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Order not found'
        })
