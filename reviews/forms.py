from django import forms
from .models import Review
from django.core.validators import MaxLengthValidator


class ReviewForm(forms.ModelForm):
    # Поля для имени и фамилии отдельно (объединим в author)
    first_name = forms.CharField(
        max_length=50,
        label='First name',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name',
            'required': 'required'
        })
    )

    last_name = forms.CharField(
        max_length=50,
        required=False,
        label='Last name',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name',
        })
    )

    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
            'required': 'required'
        })
    )

    # Переопределяем поле text с ограничением символов
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Your review (no more than 150 characters)',
            'maxlength': '150'
        }),
        label='Отзыв',
        validators=[MaxLengthValidator(150)]
    )

    # Поле для рейтинга
    rating = forms.IntegerField(
        widget=forms.HiddenInput(),
        initial=5
    )

    # Согласие с политикой
    agree = forms.BooleanField(
        label='I agree with the privacy policy',
        required=True,
        error_messages={'required': 'You must agree to the terms and conditions'}
    )

    class Meta:
        model = Review
        fields = ['first_name', 'last_name', 'email', 'text', 'rating', 'image', 'agree']
        exclude = ['author', 'is_published']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Настраиваем поле image из модели (не переопределяем отдельно)
        self.fields['image'].required = False
        self.fields['image'].label = 'Your photo'
        self.fields['image'].widget.attrs.update({
            'class': 'simple-file-input',
            'id': 'id_image',
            'accept': 'image/*',
            'style': 'display: none;'
        })

    def clean(self):
        cleaned_data = super().clean()
        # Объединяем имя и фамилию в author
        first_name = cleaned_data.get('first_name', '')
        last_name = cleaned_data.get('last_name', '')

        if first_name:
            if last_name:
                cleaned_data['author'] = f"{first_name} {last_name}"
            else:
                cleaned_data['author'] = first_name

        # Проверяем согласие
        if not cleaned_data.get('agree'):
            raise forms.ValidationError("You must agree to the terms and conditions")

        return cleaned_data

    def save(self, commit=True):
        # Не сохраняем напрямую в базу, т.к. is_published=False по умолчанию
        instance = super().save(commit=False)
        instance.author = self.cleaned_data['author']
        instance.is_published = False  # Отзыв требует модерации

        if commit:
            instance.save()
        return instance
