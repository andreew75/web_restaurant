from django import forms


class SearchForm(forms.Form):
    q = forms.CharField(
        label='',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Type Your Search Words',
            'name': 'q',
            'value': '',
        })
    )