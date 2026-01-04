from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import datetime
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
import re


class ReservationForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Name',
            'data-label': 'Your Name',
        }),
        label='Name',
        error_messages={
            'required': 'Your Name field is empty'
        }
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
            'data-label': 'Email',
        }),
        label='Email',
        error_messages={
            'required': 'Email field is empty',
            'invalid': 'Please enter a valid email address'
        }
    )

    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 XXX XXX XX XX',
            'data-label': 'Phone Number',
        }),
        label='Phone Number',
        error_messages={
            'required': 'Phone field is empty',
            'invalid': 'Please enter a valid phone number'
        }

    )

    guests = forms.ChoiceField(
        choices=[
            ('', 'Guests'),
            (1, '1 people'),
            (2, '2 People'),
            (3, '3 People'),
            (4, '4 People'),
            (5, '5 People'),
            (6, '6 People'),
            (8, 'more than 6 People'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'headernum',
            'data-label': 'Guests'
        }),
        label='Guests',
        error_messages={
            'required': 'Select the number of guests',
        }
    )

    visit_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control js-date',
            'type': 'text',
            'min': datetime.date.today().isoformat(),
            'data-label': 'Date',
            'placeholder': 'Date',
        },
            format='%d/%m/%Y'
        ),
        label='Date',
        error_messages={
            'required': 'Select the date',
        }
    )

    visit_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control js-time',
            'type': 'text',
            'data-label': 'Time',
            'placeholder': 'Time',
        }),
        label='Time',
        error_messages={
            'required': 'Select the time',
        }
    )

    special_request = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '2',
            'placeholder': 'Add a special request (optional)',
            'data-label': 'Special wishes',
        }),
        label='Special wishes'
    )

    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox(
            attrs={
                'data-theme': 'light',
                'data-size': 'normal',
                'data-label': 'ReCaptcha',
            }
        ),
        label='',
        error_messages={
            'required': 'ReCaptcha field is empty',
        }
    )

    def clean_visit_date(self):
        visit_date = self.cleaned_data['visit_date']
        if visit_date < timezone.now().date():
            raise forms.ValidationError("The date cannot be in the past")
        return visit_date

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')

        # Очищаем номер от пробелов и дефисов
        phone_clean = re.sub(r'[\s\-\(\)]', '', phone)

        # Проверяем российский формат: +7XXXXXXXXXX
        if phone_clean.startswith('+7'):
            phone_clean = phone_clean[2:]  # Убираем +7
        elif phone_clean.startswith('7'):
            phone_clean = phone_clean[1:]  # Убираем 7
        elif phone_clean.startswith('8'):
            phone_clean = phone_clean[1:]  # Убираем 8

        # Проверяем, что остались только цифры и их 10 штук
        if not phone_clean.isdigit() or len(phone_clean) != 10:
            raise forms.ValidationError(
                'Введите номер телефона в формате: +7 XXX XXX XX XX'
            )

        # Форматируем номер для отображения
        formatted = f"+7 {phone_clean[:3]} {phone_clean[3:6]} {phone_clean[6:8]} {phone_clean[8:]}"
        return formatted
