from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid
from model_utils import FieldTracker


class Order(models.Model):
    """Модель заказа"""

    # Статусы заказа
    STATUS_NEW = 'new'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_PREPARING = 'preparing'
    STATUS_DELIVERING = 'delivering'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_NEW, 'Новый'),
        (STATUS_CONFIRMED, 'Подтвержден'),
        (STATUS_PREPARING, 'Готовится'),
        (STATUS_DELIVERING, 'В доставке'),
        (STATUS_COMPLETED, 'Выполнен'),
        (STATUS_CANCELLED, 'Отменен'),
    ]

    # Способы доставки
    DELIVERY_COURIER = 'courier'
    DELIVERY_PICKUP = 'pickup'

    DELIVERY_CHOICES = [
        (DELIVERY_COURIER, 'Курьер'),
        (DELIVERY_PICKUP, 'Самовывоз'),
    ]

    # Способы оплаты
    PAYMENT_CASH = 'cash'
    PAYMENT_CARD = 'card'

    PAYMENT_CHOICES = [
        (PAYMENT_CASH, 'Наличные'),
        (PAYMENT_CARD, 'Банковская карта'),
    ]

    # Основные поля
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    # Данные покупателя
    customer_name = models.CharField('Имя покупателя', max_length=100)
    delivery_address = models.TextField('Адрес доставки', blank=True, null=True)
    phone_number = models.CharField('Номер телефона', max_length=20)

    # Статус и детали заказа
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW
    )
    delivery_method = models.CharField(
        'Способ доставки',
        max_length=20,
        choices=DELIVERY_CHOICES,
        default=DELIVERY_COURIER
    )
    payment_method = models.CharField(
        'Способ оплаты',
        max_length=20,
        choices=PAYMENT_CHOICES,
        default=PAYMENT_CASH
    )

    # Финансовые поля
    delivery_cost = models.DecimalField(
        'Стоимость доставки',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    total_cost = models.DecimalField(
        'Общая стоимость (без скидки)',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    discount = models.DecimalField(
        'Скидка',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    final_cost = models.DecimalField(
        'Итоговая стоимость (к оплате)',
        max_digits=10,
        decimal_places=2,
        default=0
    )

    # Купон и подтверждение
    coupon_code = models.CharField('Код купона', max_length=50, blank=True, null=True)
    is_confirmed = models.BooleanField('Подтвержден по SMS', default=False)
    sms_code = models.CharField('Код подтверждения (хэш)', max_length=128, blank=True, null=True)
    sms_code_sent_at = models.DateTimeField('Код отправлен', blank=True, null=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.id.hex[:8]} от {self.created_at.strftime('%d.%m.%Y %H:%M')}"

    def save(self, *args, **kwargs):
        # Автоматически заполняем адрес доставки для самовывоза
        if self.delivery_method == self.DELIVERY_PICKUP and not self.delivery_address:
            self.delivery_address = "Самовывоз из ресторана"

        # Рассчитываем финальную стоимость при сохранении
        if self.pk:  # только для существующих записей
            self.final_cost = self.total_cost - self.discount + self.delivery_cost
        super().save(*args, **kwargs)

    def calculate_delivery_cost(self):
        """Рассчитывает стоимость доставки"""
        # Фиксированная стоимость доставки
        FIXED_DELIVERY_COST = 5
        # Порог бесплатной доставки
        FREE_DELIVERY_THRESHOLD = 100

        if self.delivery_method == self.DELIVERY_PICKUP:
            return 0

        if self.total_cost >= FREE_DELIVERY_THRESHOLD:
            return 0

        return FIXED_DELIVERY_COST

    def update_delivery_cost(self):
        """Обновляет поле delivery_cost"""
        self.delivery_cost = self.get_delivery_cost()
        self.save(update_fields=['delivery_cost', 'final_cost'])

    # Трекер для отслеживания изменений полей
    tracker = FieldTracker()


class OrderItem(models.Model):
    """Позиция в заказе"""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ'
    )

    # Ссылка на модель блюда из приложения menu
    dish = models.ForeignKey(
        'menu.MenuItem',
        on_delete=models.PROTECT,
        verbose_name='Блюдо',
        related_name='order_items'
    )

    quantity = models.PositiveIntegerField(
        'Количество',
        validators=[MinValueValidator(1)],
        default=1
    )

    price_at_order = models.DecimalField(
        'Цена на момент заказа',
        max_digits=10,
        decimal_places=2
    )

    # Дополнительные поля из MenuItem для сохранения на момент заказа
    dish_name = models.CharField('Название блюда', max_length=200, blank=True)

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f"{self.dish.name} x {self.quantity}"

    @property
    def total_price(self):
        """Общая стоимость позиции"""
        return self.price_at_order * self.quantity

    def save(self, *args, **kwargs):
        # Сохраняем название блюда на момент заказа
        if not self.dish_name and self.dish:
            self.dish_name = self.dish.name

        # Сохраняем цену на момент заказа
        if not self.price_at_order and self.dish:
            self.price_at_order = self.dish.price

        super().save(*args, **kwargs)


class Coupon(models.Model):
    """Модель купона на скидку"""

    code = models.CharField('Код купона', max_length=50, unique=True)
    discount_percent = models.DecimalField(
        'Процент скидки',
        max_digits=5,
        decimal_places=0,
        validators=[MinValueValidator(0)]
    )
    discount_amount = models.DecimalField(
        'Фиксированная сумма скидки',
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    is_active = models.BooleanField('Активен', default=True)
    valid_from = models.DateTimeField('Действует с')
    valid_until = models.DateTimeField('Действует до')
    max_uses = models.PositiveIntegerField('Максимум использований', default=1)
    times_used = models.PositiveIntegerField('Использован раз', default=0)

    class Meta:
        verbose_name = 'Купон'
        verbose_name_plural = 'Купоны'

    def __str__(self):
        return f"Купон {self.code} ({self.discount_percent}%)"

    def is_valid(self, order_amount=None):
        """Проверяет, действителен ли купон"""
        now = timezone.now()

        if not (
                self.is_active and
                self.valid_from <= now <= self.valid_until and
                self.times_used < self.max_uses
        ):
            return False

        if order_amount is not None and order_amount <= 0:
            return False

        return True

    def calculate_discount(self, total_amount):
        """Рассчитывает сумму скидки для заданной суммы"""
        if not self.is_valid(total_amount):
            return 0

        discount = 0
        if self.discount_amount > 0:
            discount = min(self.discount_amount, total_amount)
        elif self.discount_percent > 0:
            discount = total_amount * (self.discount_percent / 100)

        return discount

    def mark_as_used(self):
        """Отмечает купон как использованный"""
        self.times_used += 1
        if self.times_used >= self.max_uses:
            self.is_active = False
        self.save()
