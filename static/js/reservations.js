document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('reservationForm');
    const resultDiv = document.getElementById('reservation-result');

    // Функция для подсветки полей с ошибками
    function highlightErrorFields(errors) {
        // Сначала сбрасываем все подсветки
        resetFieldHighlights();

        if (!errors) return;

        // Подсвечиваем каждое поле с ошибкой
        Object.keys(errors).forEach(fieldName => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                field.classList.add('is-invalid');

                // Добавляем сообщение об ошибке под полем
                const errorMessage = errors[fieldName].join(', ');
                const errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                errorDiv.textContent = errorMessage;

                // Находим родительский контейнер для поля
                let parentContainer = field.parentElement;
                if (parentContainer.classList.contains('form-select')) {
                    // Для селектов с иконкой нужен особый обработчик
                    parentContainer = parentContainer.parentElement;
                }

                // Удаляем старое сообщение, если есть
                const oldError = parentContainer.querySelector('.invalid-feedback');
                if (oldError) {
                    oldError.remove();
                }

                parentContainer.appendChild(errorDiv);
            }
        });
    }

    // Функция для сброса подсветки
    function resetFieldHighlights() {
        // Убираем класс is-invalid у всех полей
        form.querySelectorAll('.is-invalid').forEach(field => {
            field.classList.remove('is-invalid');
        });

        // Удаляем все сообщения об ошибках
        form.querySelectorAll('.invalid-feedback').forEach(errorDiv => {
            errorDiv.remove();
        });
    }

    // Добавляем валидацию телефона при вводе
    const phoneField = form.querySelector('input[name="phone"]');
    if (phoneField) {
        phoneField.addEventListener('blur', function() {
            const phoneValue = this.value.replace(/\D/g, ''); // Убираем всё кроме цифр

            // Проверяем минимальное количество цифр (10 для России без кода страны)
            if (phoneValue.length > 0 && phoneValue.length < 10) {
                this.classList.add('is-invalid');
                const errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                errorDiv.textContent = 'Номер телефона должен содержать не менее 10 цифр';

                const oldError = this.parentElement.querySelector('.invalid-feedback');
                if (oldError) {
                    oldError.remove();
                }

                this.parentElement.appendChild(errorDiv);
            } else if (phoneValue.length >= 10) {
                this.classList.remove('is-invalid');
                const oldError = this.parentElement.querySelector('.invalid-feedback');
                if (oldError) {
                    oldError.remove();
                }
            }
        });

        // Форматирование телефона при вводе (необязательная опция)
        phoneField.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');

            // Форматируем как +7 XXX XXX XX XX
            if (value.length > 0) {
                let formatted = '+7';
                if (value.length > 1) {
                    formatted += ' ' + value.substring(1, 4);
                }
                if (value.length > 4) {
                    formatted += ' ' + value.substring(4, 7);
                }
                if (value.length > 7) {
                    formatted += ' ' + value.substring(7, 9);
                }
                if (value.length > 9) {
                    formatted += ' ' + value.substring(9, 11);
                }
                e.target.value = formatted;
            }
        });
    }

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        // Сбрасываем подсветку перед новой проверкой
        resetFieldHighlights();

        // Дополнительная проверка телефона перед отправкой
        let hasPhoneError = false;
        if (phoneField) {
            const phoneValue = phoneField.value.replace(/\D/g, '');
            if (phoneValue.length > 0 && phoneValue.length < 10) {
                phoneField.classList.add('is-invalid');
                const errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                errorDiv.textContent = 'Номер телефона должен содержать не менее 10 цифр';
                phoneField.parentElement.appendChild(errorDiv);
                hasPhoneError = true;
            }
        }

        // Если есть ошибка в телефоне, не отправляем форму
        if (hasPhoneError) {
            resultDiv.innerHTML = `
                <div class="alert alert-danger">
                    Пожалуйста, исправьте ошибку в номере телефона
                </div>
            `;
            return;
        }

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Отправка...';
        submitBtn.disabled = true;

        const formData = new FormData(form);

        fetch('/reservations/create-reservation/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Ответ:', data);

            if (data.success) {
                resultDiv.innerHTML = `
                    <div class="alert alert-success">
                        ${data.message}
                    </div>
                `;

                form.reset();

                // Сбрасываем подсветку при успешной отправке
                resetFieldHighlights();

                // Закрываем модальное окно через 3 секунды
                setTimeout(() => {
                    $('#reservationModule').modal('hide');

                    setTimeout(() => {
                        resultDiv.innerHTML = '';
                    }, 5000);
                }, 3000);
            } else {
                // Подсвечиваем поля с ошибками, полученными с сервера
                highlightErrorFields(data.errors);

                let errorHtml = '<div class="alert alert-danger"><ul>';
                if (data.errors) {
                    for (const field in data.errors) {
                        data.errors[field].forEach(error => {
                            errorHtml += `<li>${error}</li>`;
                        });
                    }
                } else {
                    errorHtml += `<li>${data.message}</li>`;
                }
                errorHtml += '</ul></div>';
                resultDiv.innerHTML = errorHtml;
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            resultDiv.innerHTML = `
                <div class="alert alert-danger">
                    Ошибка отправки. Проверьте консоль браузера (F12).
                </div>
            `;
        })
        .finally(() => {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        });
    });

    // Сбрасываем подсветку при изменении поля
    form.querySelectorAll('input, select, textarea').forEach(field => {
        field.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                this.classList.remove('is-invalid');
                const errorDiv = this.parentElement.querySelector('.invalid-feedback');
                if (errorDiv) {
                    errorDiv.remove();
                }
            }
        });

        field.addEventListener('change', function() {
            if (this.classList.contains('is-invalid')) {
                this.classList.remove('is-invalid');
                const errorDiv = this.parentElement.querySelector('.invalid-feedback');
                if (errorDiv) {
                    errorDiv.remove();
                }
            }
        });
    });
});