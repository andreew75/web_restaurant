document.addEventListener('DOMContentLoaded', function () {

    const URLS = {
    cartUpdate: '/orders/cart/update/',
    cartRemove: '/orders/cart/remove/',
    updateTotals: '/orders/cart/update-totals/',
    applyCoupon: '/orders/cart/apply-coupon/',
    checkout: '/orders/checkout/',
    verifySms: '/orders/verify-sms/',
    cartDetails: '/orders/cart/',
    // home: '/orders/cart/home',
};
    /* -------------------- helpers -------------------- */

    function setPrice(container, value) {
        if (!container) return;
        const el = container.querySelector('.price-value');
        if (el) el.textContent = Number(value).toFixed(2);
    }

    function updateCartCounter(count) {
        const cartCounter = document.querySelector('.cart-count');
        if (cartCounter) cartCounter.textContent = count;

        const navCounter = document.querySelector('.nav-cart-count');
        if (navCounter) navCounter.textContent = count;
    }

    /* -------------------- quantity +/- -------------------- */

    document.querySelectorAll('.quantity-change').forEach(btn => {
        btn.addEventListener('click', e => {
            e.preventDefault();

            const dishId = btn.dataset.dishId;
            const action = btn.dataset.action;
            const input = document.querySelector(`#quantity-${dishId}`);

            let qty = parseInt(input.value);

            if (action === 'increase') qty++;
            if (action === 'decrease') qty = Math.max(1, qty - 1);

            updateCartItem(dishId, qty);
        });
    });

    /* -------------------- update cart item -------------------- */

    function updateCartItem(dishId, quantity) {
        const csrf = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const fd = new FormData();
        fd.append('dish_id', dishId);
        fd.append('quantity', quantity);
        fd.append('csrfmiddlewaretoken', csrf);

        fetch(URLS.cartUpdate, {
            method: 'POST',
            body: fd
        })
        .then(r => r.json())
        .then(data => {
            if (!data.success) return;

            // quantity
            const input = document.querySelector(`#quantity-${dishId}`);
            if (input) input.value = quantity;

            // item total
            const row = document.querySelector(`#cart-item-${dishId}`);
            if (row && data.item_total !== undefined) {
                setPrice(row.querySelector('.cart-product-total'), data.item_total);
            }

            // remove if needed
            if (data.item_removed) {
                row?.remove();
            }

            updateTotals();
            updateCartCounter(data.cart_item_count);
        });
    }

    /* -------------------- remove item -------------------- */

    let pendingRemoveDishId = null;

    // открыть модалку
    document.querySelectorAll('.remove-item').forEach(btn => {
        btn.addEventListener('click', e => {
            e.preventDefault();
            pendingRemoveDishId = btn.dataset.dishId;

            document.getElementById('confirm-modal').classList.remove('hidden');
        });
    });

    // отмена
    document.getElementById('cancel-remove').addEventListener('click', () => {
        pendingRemoveDishId = null;
        document.getElementById('confirm-modal').classList.add('hidden');
    });

    // подтверждение
    document.getElementById('confirm-remove').addEventListener('click', () => {
        if (!pendingRemoveDishId) return;

        const dishId = pendingRemoveDishId;
        pendingRemoveDishId = null;

        document.getElementById('confirm-modal').classList.add('hidden');

        const csrf = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const fd = new FormData();
        fd.append('dish_id', dishId);
        fd.append('action', 'remove');
        fd.append('csrfmiddlewaretoken', csrf);

        fetch(`${URLS.cartRemove}?dish_id=${dishId}`, {
            method: 'POST',
            body: fd
        })
        .then(r => r.json())
        .then(data => {
            if (!data.success) return;

            if (data.cart_item_count === 0) {
                window.location.href = URLS.cartDetails;
                return;
            }

            document.getElementById(`cart-item-${dishId}`)?.remove();
            updateTotals();
            updateCartCounter(data.cart_item_count);
        });
    });

    /* -------------------- totals / coupon -------------------- */

    function updateTotals() {
        fetch(URLS.updateTotals, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })

        .then(r => r.json())
        .then(data => {
            document.querySelectorAll('.total-cost-order .price-value')
                .forEach(el => el.textContent = data.cart_subtotal.toFixed(2));
            if (!data.success) return;

            const rows = document.querySelectorAll('.cart-total-amount li');

            rows.forEach(li => {
                if (li.textContent.includes('Subtotal'))
                    setPrice(li, data.cart_subtotal);

                if (li.textContent.includes('Discount'))
                    setPrice(li, data.discount || 0);

                if (li.textContent.includes('Delivery'))
                    setPrice(li, data.delivery_cost);

                if (li.textContent.includes('Order Total'))
                    setPrice(li, data.order_total);
            });
                // Обновляем сообщения примененной скидке
            function updateDiscount(discount) {
                const discountRow = document.querySelector('.cart-discount');

                if (!discountRow) return;

                if (Number(discount) > 0) {
                    discountRow.style.display = '';
                    discountRow.querySelector('.price-value').textContent =
                        Number(discount).toFixed(2);
                } else {
                    discountRow.style.display = 'none';
                }
            }

                // Обновляем сообщения стоимости о доставки
            function updateDeliveryMessage(totalPrice, threshold, fixedCost) {
                const messageElement = document.querySelector('.total-cost-order p');

                if (!messageElement) return;

                if (totalPrice < threshold) {
                    messageElement.textContent =
                        `Order amount less than $ ${threshold}. Delivery will be charged $ ${fixedCost}.`;
                    messageElement.style.color = '';
                } else {
                    messageElement.textContent = 'The order will be delivered free of charge.';
                    messageElement.style.color = '#c59d5f';
                }
            }
            updateDiscount(data.discount);

            updateDeliveryMessage(
                data.cart_subtotal,
                data.free_delivery_threshold,
                data.fixed_delivery_cost
            );
        });
    }

    /* -------------------- coupon submit -------------------- */

    const couponForm = document.getElementById('coupon-form');
    const couponError = document.querySelector('.coupon-error');
    if (couponForm) {
        couponForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const formData = new FormData(this);

        fetch(this.action, {
            method: 'POST',
            body: formData
        })
        .then(r => r.json())
        .then(data => {
            if (!data.success) {
                couponError.textContent = data.message;
                couponError.style.display = 'block';
                return;
            }

            // успех
            couponError.style.display = 'none';
            couponError.textContent = '';

            updateTotals();
        });
    });
}

    /* -------------------- phone mask +7 XXX XXX XX XX -------------------- */

    const phoneInput = document.getElementById('phone');

    if (phoneInput) {
        phoneInput.addEventListener('input', () => {
            let digits = phoneInput.value.replace(/\D/g, '');

            if (digits.startsWith('7')) digits = digits.slice(1);
            digits = digits.substring(0, 10);

            let result = '+7';

            if (digits.length > 0) result += ' ' + digits.substring(0, 3);
            if (digits.length >= 4) result += ' ' + digits.substring(3, 6);
            if (digits.length >= 7) result += ' ' + digits.substring(6, 8);
            if (digits.length >= 9) result += ' ' + digits.substring(8, 10);

            phoneInput.value = result;
        });
    }
    updateTotals();

    // ===== CHECKOUT LOGIC =====

    // Обработка кнопки Confirm Order
    const confirmBtn = document.getElementById('confirm-order-btn');
    const checkoutForm = document.getElementById('checkout-form');
    const agreeCheckbox = document.getElementById('agree');
    const smsSection = document.getElementById('sms-verification-section');
    const verifyBtn = document.getElementById('verify-sms-btn');
    const smsInput = document.getElementById('sms');

    // Обработка кнопки Confirm Order
    if (confirmBtn && checkoutForm) {
        confirmBtn.addEventListener('click', function(e) {
            e.preventDefault();

            // Проверяем форму
            if (!validateCheckoutForm()) {
                return;
            }

            // Отправляем запрос на создание заказа
            sendCheckoutRequest();
        });
    }

    // Обработка кнопки Verify SMS
    if (verifyBtn && smsInput) {
        verifyBtn.addEventListener('click', function() {
            verifySmsCode();
        });

        // Enter для отправки кода
        smsInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                verifySmsCode();
            }
        });
    }

    // Валидация формы checkout (только проверка заполненности)
    function validateCheckoutForm() {
        const nameField = document.getElementById('name');
        const phoneField = document.getElementById('phone');
        const addressField = document.getElementById('address');

        let isValid = true;

        // Проверка имени
        if (!nameField.value.trim()) {
            nameField.style.borderColor = 'red';
            isValid = false;
        } else {
            nameField.style.borderColor = '';
        }

        // Проверка телефона (только наличие)
        if (!phoneField.value.trim()) {
            phoneField.style.borderColor = 'red';
            isValid = false;
        } else {
            phoneField.style.borderColor = '';
        }

        // Проверка адреса (всегда требуется, так как только курьер)
        if (!addressField.value.trim()) {
            addressField.style.borderColor = 'red';
            isValid = false;
        } else {
            addressField.style.borderColor = '';
        }

        // Проверка согласия
        if (!agreeCheckbox || !agreeCheckbox.checked) {
            // showMessage('Please agree to the Terms and Privacy Policy', 'error');
            isValid = false;
        }

        return isValid;
    }

    // Отправка запроса на создание заказа
    function sendCheckoutRequest() {
        const formData = new FormData(document.getElementById('checkout-form'));
        formData.append('agree', document.getElementById('agree').checked ? 'true' : '');
        formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

        // Показываем индикатор загрузки
        const confirmBtn = document.getElementById('confirm-order-btn');
        const originalText = confirmBtn.textContent;
        confirmBtn.textContent = 'Sending...';
        confirmBtn.disabled = true;

        fetch(URLS.checkout, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            confirmBtn.textContent = originalText;
            confirmBtn.disabled = false;

            if (data.success) {
                // Скрываем форму и показываем SMS секцию
                document.getElementById('confirm-order-btn').style.display = 'none';
                document.getElementById('agree').closest('.form-check').style.display = 'none';

                const smsSection = document.getElementById('sms-verification-section');
                if (smsSection) {
                    smsSection.classList.remove('hidden');
                    document.getElementById('sms').focus();
                }

                // showMessage(data.message, 'success');
            } else {
                // showMessage(data.message, 'error');
            }
        })
        .catch(error => {
            confirmBtn.textContent = originalText;
            confirmBtn.disabled = false;

        });
    }

    // Проверка SMS кода
    function verifySmsCode() {
    const smsInput = document.getElementById('sms');
    const errorBox = document.querySelector('.sms-error');

    const code = smsInput.value.trim();

    // очистка старой ошибки
    errorBox.style.display = 'none';
    errorBox.textContent = '';

    // frontend-проверка
    if (!code || code.length !== 4 || !/^\d+$/.test(code)) {
        errorBox.textContent = 'Please enter a valid 4-digit code';
        errorBox.style.display = 'block';
        return;
    }

    const formData = new FormData();
    formData.append('sms_code', code);

    fetch('/orders/verify-sms/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(r => r.json())
    .then(data => {
        if (!data.success) {
            // 🔥 вот тут используется сообщение из views.py
            errorBox.textContent = data.message || 'Invalid code';
            errorBox.style.display = 'block';
            return;
        }

        // успех
        errorBox.style.display = 'none';
        showOrderConfirmation();
    })
    .catch(() => {
        errorBox.textContent = 'Something went wrong. Please try again.';
        errorBox.style.display = 'block';
    });
}


    // Показ сообщения об успешном оформлении заказа
    function showOrderConfirmation() {
        // Создаем модальное окно
        const modal = document.getElementById('order-confirmation-modal');
        if (modal) {
            modal.classList.remove('hidden');

            // // Автоматический редирект на главную через 10 секунд
            // setTimeout(() => {
            //     window.location.href = URLS.home;
            // }, 10000);
        }
    }
});