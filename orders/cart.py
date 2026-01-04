from decimal import Decimal
from django.conf import settings


class Cart:
    """Класс для работы с корзиной в сессии"""

    def __init__(self, request):
        """Инициализация корзины"""
        self.request = request
        self.session = request.session

        # Получаем корзину из сессии или создаем новую
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Сохраняем пустую корзину в сессии
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, dish, quantity=1, override_quantity=False):
        """
        Добавить блюдо в корзину или обновить его количество

        Args:
            dish: объект MenuItem
            quantity: количество (по умолчанию 1)
            override_quantity: заменить количество (True) или добавить к существующему (False)
        """
        dish_id = str(dish.id)

        if dish_id not in self.cart:
            self.cart[dish_id] = {
                'quantity': 0,
                'price': str(dish.price),  # Сохраняем как строку для Decimal
                'name': dish.name,
                'image': dish.image.url if dish.image else '',
                'description': dish.description[:100] if dish.description else '',  # Сохраняем краткое описание
                'cooking_time': dish.cooking_time,
            }

        if override_quantity:
            self.cart[dish_id]['quantity'] = quantity
        else:
            self.cart[dish_id]['quantity'] += quantity

        # Гарантируем, что количество не меньше 1
        if self.cart[dish_id]['quantity'] < 1:
            self.cart[dish_id]['quantity'] = 1

        self.save()

    def save(self):
        """Сохранить корзину в сессии"""
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, dish):
        """
        Удалить блюдо из корзины

        Args:
            dish: объект MenuItem или ID блюда
        """
        dish_id = str(dish.id) if hasattr(dish, 'id') else str(dish)

        if dish_id in self.cart:
            del self.cart[dish_id]
            self.save()

            # если корзина стала пустой — убираем купон
            if not self.cart:
                self.session.pop('applied_coupon', None)

    def update_quantity(self, dish_id, quantity):
        """
        Обновить количество блюда в корзине

        Args:
            dish_id: ID блюда
            quantity: новое количество
        """
        dish_id = str(dish_id)

        if dish_id in self.cart:
            if quantity > 0:
                self.cart[dish_id]['quantity'] = quantity
            else:
                # Если количество 0 или меньше - удаляем позицию
                del self.cart[dish_id]
            self.save()
            return True
        return False

    def clear(self):
        """Очистить корзину"""
        # Удаляем корзину и купон из сессии
        del self.session[settings.CART_SESSION_ID]
        self.session.pop('applied_coupon', None)
        self.session.modified = True

    def get_total_price(self):
        """Получить общую стоимость всех товаров в корзине"""
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def get_cart_subtotal(self):
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def get_delivery_cost(self, delivery_method='courier', cart_total=None):
        """
        Рассчитать стоимость доставки
        """
        if cart_total is None:
            cart_total = self.get_total_price()

        # Константы доставки
        FIXED_DELIVERY_COST = 5  # Фиксированная стоимость доставки
        FREE_DELIVERY_THRESHOLD = 100  # Порог бесплатной доставки

        if delivery_method == 'pickup':
            return Decimal('0')

        if cart_total >= FREE_DELIVERY_THRESHOLD:
            return Decimal('0')

        return Decimal(str(FIXED_DELIVERY_COST))

    def get_final_price(self, discount=0, delivery_method='courier'):
        """
        Получить итоговую стоимость с учетом скидки и доставки

        Args:
            discount: сумма скидки
            delivery_method: способ доставки
        """
        total = self.get_total_price()
        delivery_cost = self.get_delivery_cost(delivery_method, total)
        return total - Decimal(str(discount)) + delivery_cost

    def get_items_with_details(self):
        """
        Получить товары из корзины с детальной информацией

        Возвращает список словарей с полной информацией о каждом блюде
        """
        from menu.models import MenuItem  # Импортируем здесь, чтобы избежать циклического импорта

        items = []
        dish_ids = self.cart.keys()

        # Получаем все блюда из базы данных одним запросом
        dishes = MenuItem.objects.filter(id__in=dish_ids)
        dish_dict = {str(dish.id): dish for dish in dishes}

        for dish_id, item_data in self.cart.items():
            dish = dish_dict.get(dish_id)
            if dish:
                item = {
                    'dish': dish,
                    'dish_id': dish_id,
                    'quantity': item_data['quantity'],
                    'price': Decimal(item_data['price']),
                    'name': item_data['name'],
                    'image': item_data.get('image', ''),
                    'description': item_data.get('description', ''),
                    'cooking_time': item_data.get('cooking_time', 15),
                    'total_price': Decimal(item_data['price']) * item_data['quantity'],
                }
                items.append(item)

        return items

    def get_item_count(self):
        """Получить общее количество товаров в корзине"""
        return sum(item['quantity'] for item in self.cart.values())

    def get_unique_item_count(self):
        """Получить количество уникальных товаров в корзине"""
        return len(self.cart)

    def is_empty(self):
        """Проверка, пуста ли корзина"""
        return len(self.cart) == 0

    def __len__(self):
        """Возвращает общее количество товаров в корзине"""
        return self.get_item_count()

    def __iter__(self):
        """
        Итератор по товарам в корзине.
        Позволяет использовать корзину в циклах for.
        """
        items = self.get_items_with_details()
        for item in items:
            yield item
