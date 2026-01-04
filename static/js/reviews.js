document.addEventListener('DOMContentLoaded', function() {
    // 1. Счетчик символов для текстового поля
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

    // 2. Анимация звезд
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

    // 3. Инициализация загрузки фото
    initPhotoUpload();
});

// Функция для инициализации загрузки фото
function initPhotoUpload() {
    console.log('Initializing photo upload...');

    const fileInput = document.getElementById('id_image');
    const uploadButton = document.getElementById('uploadButton');

    if (!fileInput || !uploadButton) {
        console.error('File input or upload button not found!');
        console.log('fileInput:', fileInput);
        console.log('uploadButton:', uploadButton);
        return;
    }

    const btnDefault = uploadButton.querySelector('.btn-default-primary');
    const btnSelected = uploadButton.querySelector('.btn-selected');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');

    // Обработчик выбора файла
    fileInput.addEventListener('change', function() {
        console.log('File input changed, files:', this.files);

        if (this.files && this.files[0]) {
            const file = this.files[0];
            console.log('File selected:', file.name, file.size, file.type);

            // Проверка типа файла
            if (!file.type.match('image.*')) {
                alert('Please select an image file (JPG, PNG, GIF)');
                resetFileInput();
                return;
            }

            // Проверка размера (5MB)
            if (file.size > 5 * 1024 * 1024) {
                alert('File size should be less than 5MB');
                resetFileInput();
                return;
            }

            // Обновляем информацию о файле
            updateFileInfo(file);

            // Показываем состояние с выбранным файлом
            showSelectedState();
        } else {
            // Если файл не выбран, показываем исходное состояние
            console.log('No file selected');
            showDefaultState();
        }
    });

    // Функция обновления информации о файле
    function updateFileInfo(file) {
        if (fileName) {
            // Обрезаем длинное имя файла
            const name = file.name;
            const maxLength = 20;

            if (name.length > maxLength) {
                const extension = name.split('.').pop();
                const nameWithoutExt = name.substring(0, name.lastIndexOf('.'));
                const truncatedName = nameWithoutExt.substring(0, maxLength - extension.length - 3);
                fileName.textContent = truncatedName + '...' + extension;
                fileName.title = name; // Полное имя в title
            } else {
                fileName.textContent = name;
                fileName.title = '';
            }
        }

        if (fileSize) {
            fileSize.textContent = formatFileSize(file.size);
        }
    }

    // Функция показа состояния с выбранным файлом
    function showSelectedState() {
        console.log('Showing selected state');
        if (btnDefault) btnDefault.style.display = 'none';
        if (btnSelected) btnSelected.style.display = 'flex';
        uploadButton.classList.add('has-file');
    }

    // Функция показа исходного состояния
    function showDefaultState() {
        console.log('Showing default state');
        if (btnDefault) btnDefault.style.display = 'flex';
        if (btnSelected) btnSelected.style.display = 'none';
        uploadButton.classList.remove('has-file');
    }

    // Функция сброса выбора файла
    function resetFileInput() {
        console.log('Resetting file input');
        fileInput.value = '';
        showDefaultState();
    }

    // Вспомогательная функция для форматирования размера файла
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    // Добавляем возможность сброса файла по двойному клику
    uploadButton.addEventListener('dblclick', function(e) {
        e.preventDefault();
        if (fileInput.value) {
            resetFileInput();
        }
    });

    console.log('Photo upload initialized successfully');

    // Модальное окно отзыва

    const popup = document.getElementById('simplePopup');

    if (!popup) return;

    const shouldShow = popup.dataset.show === '1';
    const redirectUrl = popup.dataset.redirectUrl;

    if (shouldShow) {
        setTimeout(() => {
            popup.style.display = 'block';
            document.body.style.overflow = 'hidden';
        }, 100);

        // авто-редирект через 5 сек
        setTimeout(() => {
            if (redirectUrl) {
                window.location.href = redirectUrl;
            }
        }, 5000);
    }

    const okBtn = document.getElementById('popup-ok-btn');
    if (okBtn) {
        okBtn.addEventListener('click', () => {
            popup.style.display = 'none';
            document.body.style.overflow = 'auto';

            if (redirectUrl) {
                window.location.href = redirectUrl;
            }
        });
    }
}