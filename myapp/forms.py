from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Item

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, help_text='Obrigatorio.')
    last_name = forms.CharField(max_length=30, help_text='Obrigatorio.')
    email = forms.EmailField(max_length=254, help_text='Obrigatorio. Informe um endereco de email valido.')
    phone_number = forms.RegexField(max_length=11, regex=r'^\d{10,11}$',
                                error_message = ("Numero de telefone precisa estar no formato: 'DDD999999999'. Ate 11 digitos."))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'phone_number', 'email', 'password1', 'password2', )

class ItemForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = ('title', 'description', 'price')
