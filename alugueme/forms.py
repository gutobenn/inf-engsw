# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import Item, Rent

def validate_email(value):
    if not value.endswith('@inf.ufrgs.br'):
        raise ValidationError(
            _('Seu e-mail deve ser @inf.ufrgs.br')
        )

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, help_text='Obrigatório.', label='Nome')
    last_name = forms.CharField(max_length=30, help_text='Obrigatório.', label='Sobrenome')
    email = forms.EmailField(max_length=254, help_text='Obrigatório. Informe um endereço de e-mail válido.', validators=[validate_email])
    phone_number = forms.RegexField(max_length=11, regex=r'^\d{10,11}$',
                                error_messages = {'required':"Número de telefone precisa estar no formato: 'DDD999999999'. Até 11 digitos."},
                                label='Telefone')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'phone_number', 'email', 'password1', 'password2', )

class ItemForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = ('title', 'description', 'price', 'image')

class SearchItemForm(forms.Form):
    search_text = forms.CharField(
                    required = False,
                    label='',
                    widget=forms.TextInput(attrs={'placeholder': 'Eu quero...'})
                  )
    search_price_min = forms.IntegerField(
                    required = False,
                    label='Preço entre R$',
                    widget = forms.TextInput(attrs={'size': 4, 'maxlength':4})
                    )
    search_price_max = forms.IntegerField(
                    required = False,
                    label='e R$',
                    widget = forms.TextInput(attrs={'size': 4, 'maxlength':4})
                    )

    search_onlyavailable = forms.BooleanField(
                    initial=True,
                    required = False,
                    label='Exibir apenas itens disponíveis',
                    widget = forms.CheckboxInput()
                    )


class RentForm(forms.ModelForm):

    class Meta:
        model = Rent
        fields = ('months', 'payment')
