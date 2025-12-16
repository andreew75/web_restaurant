document.addEventListener('DOMContentLoaded', function() {
        const slides = document.querySelectorAll('.slide');
        const prevButton = document.querySelector('.slider-nav.prev');
        const nextButton = document.querySelector('.slider-nav.next');
        const indicators = document.querySelectorAll('.indicator');
        let currentSlide = 0;
        let slideInterval;
        const slideDuration = 5000; // 5 секунд

        // Функция для перехода к конкретному слайду
        function goToSlide(n) {
            slides[currentSlide].classList.remove('active');
            indicators[currentSlide].classList.remove('active');

            currentSlide = (n + slides.length) % slides.length;

            slides[currentSlide].classList.add('active');
            indicators[currentSlide].classList.add('active');
        }

        // Функция для перехода к следующему слайду
        function nextSlide() {
            goToSlide(currentSlide + 1);
        }

        // Функция для перехода к предыдущему слайду
        function prevSlide() {
            goToSlide(currentSlide - 1);
        }

        // Автопрокрутка слайдов
        function startAutoSlide() {
            // Очищаем предыдущий интервал, если он существует
            if (slideInterval) {
                clearInterval(slideInterval);
            }
            slideInterval = setInterval(nextSlide, slideDuration);
        }

        // Остановка автопрокрутки
        function stopAutoSlide() {
            if (slideInterval) {
                clearInterval(slideInterval);
                slideInterval = null; // Важно: обнуляем переменную
            }
        }

        // Обработчики событий для кнопок навигации
        nextButton.addEventListener('click', function() {
            nextSlide();
            stopAutoSlide();
            startAutoSlide();
        });

        prevButton.addEventListener('click', function() {
            prevSlide();
            stopAutoSlide();
            startAutoSlide();
        });

        // Обработчики событий для индикаторов
        indicators.forEach(indicator => {
            indicator.addEventListener('click', function() {
                const slideIndex = parseInt(this.getAttribute('data-slide'));
                goToSlide(slideIndex);
                stopAutoSlide();
                startAutoSlide();
            });
        });

        // Пауза автопрокрутки при наведении на слайдер
        const sliderContainer = document.querySelector('.slider-container');
        sliderContainer.addEventListener('mouseenter', stopAutoSlide);
        sliderContainer.addEventListener('mouseleave', startAutoSlide);

        // Инициализация автопрокрутки
        startAutoSlide();
    });