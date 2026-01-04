document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('reservationForm');
    const resultDiv = document.getElementById('reservation-result');

    /* =========================
       FLATPICKR
       ========================= */

    flatpickr('.js-date', {
        altInput: true,
        altFormat: 'd-m-Y',
        dateFormat: 'Y-m-d',
        minDate: 'today',
        allowInput: true
    });

    flatpickr('.js-time', {
        enableTime: true,
        noCalendar: true,
        dateFormat: 'H:i',
        time_24hr: true,
        allowInput: true
    });

    /* =========================
       ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
       ========================= */

    function highlightErrorFields(errors) {
        resetFieldHighlights();
        if (!errors) return;

        Object.keys(errors).forEach(fieldName => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (!field) return;

            field.classList.add('is-invalid');

            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.textContent = errors[fieldName].join(', ');

            const oldError = field.parentElement.querySelector('.invalid-feedback');
            if (oldError) oldError.remove();

            field.parentElement.appendChild(errorDiv);
        });
    }

    function resetFieldHighlights() {
        form.querySelectorAll('.is-invalid').forEach(f => f.classList.remove('is-invalid'));
        form.querySelectorAll('.invalid-feedback').forEach(e => e.remove());
    }

    /* =========================
       ВАЛИДАЦИЯ ТЕЛЕФОНА
       ========================= */

    const phoneField = form.querySelector('input[name="phone"]');

    if (phoneField) {
        phoneField.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (!value) return;

            let formatted = '+7';
            if (value.length > 1) formatted += ' ' + value.substring(1, 4);
            if (value.length > 4) formatted += ' ' + value.substring(4, 7);
            if (value.length > 7) formatted += ' ' + value.substring(7, 9);
            if (value.length > 9) formatted += ' ' + value.substring(9, 11);

            e.target.value = formatted;
        });
    }

    /* =========================
       SUBMIT
       ========================= */

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        resetFieldHighlights();

        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');

        submitBtn.disabled = true;
        submitBtn.textContent = 'Отправка...';

        fetch('/reservations/create-reservation/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
            const overlay = document.getElementById('reservation-success-overlay');

            overlay.classList.remove('d-none');

            form.reset();
            resetFieldHighlights();

            setTimeout(() => {
                $('#reservationModule').modal('hide');

                // сброс overlay после закрытия
                setTimeout(() => {
                    overlay.classList.add('d-none');
                }, 500);
            }, 5000);
        }
        })
        .catch(() => {
            resultDiv.innerHTML = `<div class="alert alert-danger">Ошибка отправки</div>`;
        })
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Отправить';
        });
    });
});
