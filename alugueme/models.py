# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Item(models.Model):
    AVAILABLE_STATUS = 1
    UNAVAILABLE_STATUS = 2
    STATUS_CHOICES = (
        (AVAILABLE_STATUS, 'Disponível'),
        (UNAVAILABLE_STATUS, 'Indisponível'),
    )
    title = models.CharField(max_length=60, verbose_name='Título')
    description = models.TextField(max_length=800, verbose_name='Descrição')
    published_date = models.DateTimeField(blank=True, null=True)
    owner = models.ForeignKey('auth.User')
    price = models.DecimalField(max_digits=4, decimal_places=2, default=0, verbose_name='Preço')
    image = models.ImageField(upload_to = 'images/', default = 'images/None/no-img.jpg', verbose_name='Foto')
    status = models.IntegerField(choices=STATUS_CHOICES, default=AVAILABLE_STATUS)

    def __str__(self):
        return self.title

class Rent(models.Model):
    PENDING_STATUS = 1
    CANCELLED_STATUS = 2
    CONFIRMED_STATUS = 3
    STATUS_CHOICES = (
        (PENDING_STATUS, 'Pendente'),
        (CANCELLED_STATUS, 'Cancelado'),
        (CONFIRMED_STATUS, 'Confirmado'),
    )
    MONEY = 1
    TRADE = 2
    PAYMENT_CHOICES = (
        (MONEY, 'Dinheiro'),
        (TRADE, 'Troca'),
    )
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    item = models.OneToOneField(Item,on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING_STATUS)
    request_date = models.DateTimeField()
    confirmation_date = models.DateTimeField(blank=True, null=True)
    months = models.PositiveIntegerField(verbose_name='Meses', validators=[MinValueValidator(1), MaxValueValidator(6)], default=1) #TODO limit field max and min
    payment = models.IntegerField(choices=PAYMENT_CHOICES,verbose_name='Forma de pagamento')
