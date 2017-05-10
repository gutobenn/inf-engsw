# -*- coding: utf-8 -*-
from django.db import models
from easymoney import MoneyField

class Item(models.Model):
    AVAILABLE_STATUS = 1
    UNAVAILABLE_STATUS = 2
    STATUS_CHOICES = (
        (AVAILABLE_STATUS, 'Available'),
        (UNAVAILABLE_STATUS, 'Unavailable'),
    )
    title = models.CharField(max_length=60, verbose_name='Título')
    description = models.TextField(max_length=800, verbose_name='Descrição')
    published_date = models.DateTimeField(blank=True, null=True)
    owner = models.ForeignKey('auth.User')
    price = MoneyField(default=0, verbose_name='Preço')
    image = models.ImageField(upload_to = 'images/', default = 'images/None/no-img.jpg', verbose_name='Foto')
    status = models.IntegerField(choices=STATUS_CHOICES, default=AVAILABLE_STATUS)

    def __str__(self):
        return self.title
