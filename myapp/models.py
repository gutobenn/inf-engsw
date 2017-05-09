from django.db import models
from django.utils import timezone
from easymoney import MoneyField
from django.core.files.storage import FileSystemStorage
import os

class Item(models.Model):
    title = models.CharField(max_length=60)
    description = models.TextField(max_length=400)
    published_date = models.DateTimeField(blank=True, null=True)
    owner = models.ForeignKey('auth.User')
    # image = models.ImageField(upload_to='/your_image_name', storage=upload_storage) TODO add image
    price = MoneyField(default=0)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title
