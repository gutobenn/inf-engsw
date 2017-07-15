# -*- coding: utf-8 -*-
from django.contrib.auth import models as auth_models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=40, blank=True)
    course = models.CharField(max_length=40, blank=True)
    phone_number = models.CharField(max_length=12, blank=True)
    
    ## CONSTANTS
    c_max_items = models.PositiveSmallIntegerField(default=10)
    c_max_rents = models.PositiveSmallIntegerField(default=3)

    # counter for # of active announcements
    items = models.PositiveSmallIntegerField(
            validators=[MinValueValidator(0), MaxValueValidator(c_max_items)], default=0) 
    # counter for # of active announcements
    rents = models.PositiveSmallIntegerField(
            validators=[MinValueValidator(0), MaxValueValidator(c_max_rents)], default=0) 

    can_rent = models.BooleanField(default=True) # flag for rent

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

class Item(models.Model):
    AVAILABLE_STATUS = 1
    UNAVAILABLE_STATUS = 2
    INACTIVE_STATUS = 3

    STATUS_CHOICES = ((AVAILABLE_STATUS, 'Disponível'), (UNAVAILABLE_STATUS, 'Indisponível'), (INACTIVE_STATUS, "Inativo"))
    title = models.CharField(max_length=60, verbose_name='Título')
    description = models.TextField(max_length=800, verbose_name='Descrição')
    published_date = models.DateTimeField(blank=True, null=True)
    owner = models.ForeignKey(User)
    price = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0,
        verbose_name='Preço',
        validators=[MinValueValidator(0)])
    image = models.ImageField(
        upload_to='images/',
        default='images/None/no-img.jpg',
        verbose_name='Foto')
    status = models.IntegerField(
        choices=STATUS_CHOICES, default=AVAILABLE_STATUS)

    def __str__(self):
        return self.title


class Rent(models.Model):
    PENDING_STATUS = 1
    CANCELLED_STATUS = 2
    CONFIRMED_STATUS = 3
    ENDED_STATUS = 4
    DELAYED_STATUS = 5
    STATUS_CHOICES = ((PENDING_STATUS, 'Pendente'),
                      (CANCELLED_STATUS, 'Cancelado'),
                      (CONFIRMED_STATUS, 'Confirmado'),
                      (ENDED_STATUS, 'Encerrado'),
                      (DELAYED_STATUS, 'Atrasado'))
    MONEY = 1
    TRADE = 2
    PAYMENT_CHOICES = ((MONEY, 'Dinheiro'), (TRADE, 'Troca'), )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    status = models.IntegerField(
        choices=STATUS_CHOICES, default=PENDING_STATUS)
    request_date = models.DateTimeField()
    confirmation_date = models.DateTimeField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    months = models.PositiveIntegerField(
        verbose_name='Meses',
        validators=[MinValueValidator(1),
                    MaxValueValidator(6)],
        default=1)
    payment = models.IntegerField(
        choices=PAYMENT_CHOICES, verbose_name='Forma de pagamento')
