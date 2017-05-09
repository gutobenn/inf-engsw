# -*- coding: utf-8 -*-
from django.db import models
from easymoney import MoneyField
from django.core.files.storage import FileSystemStorage
import os

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
    # image = models.ImageField(upload_to='/your_image_name', storage=upload_storage) TODO add image
    price = MoneyField(default=0, verbose_name='Preço')
    status = models.IntegerField(choices=STATUS_CHOICES, default=AVAILABLE_STATUS)

    def __str__(self):
        return self.title
