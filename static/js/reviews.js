document.addEventListener('DOMContentLoaded', function() {
    // Счетчик символов для текстового поля
    const textarea = document.querySelector('textarea[name="text"]');
    const charCount = document.getElementById('charCount');

    if (textarea && charCount) {
        charCount.textContent = textarea.value.length;

        textarea.addEventListener('input', function() {
            charCount.textContent = this.value.length;

            if (this.value.length > 150) {
                charCount.classList.add('text-danger');
            } else {
                charCount.classList.remove('text-danger');
            }
        });
    }

    // Анимация звезд
    const starInputs = document.querySelectorAll('.star-rating-fa-inputs input[type="radio"]');
    const starLabels = document.querySelectorAll('.star-label-fa');

    starInputs.forEach(input => {
        input.addEventListener('change', function() {
            const value = parseInt(this.value);

            // Обновляем визуальное отображение звезд
            starLabels.forEach((label, index) => {
                if (index < value) {
                    label.querySelector('i').classList.remove('far');
                    label.querySelector('i').classList.add('fas', 'text-warning');
                } else {
                    label.querySelector('i').classList.remove('fas', 'text-warning');
                    label.querySelector('i').classList.add('far');
                }
            });
        });
    });

    // Инициализация звезд при загрузке
    const checkedStar = document.querySelector('input[name="rating"]:checked');
    if (checkedStar) {
        checkedStar.dispatchEvent(new Event('change'));
    }
});

// PopUP massage
