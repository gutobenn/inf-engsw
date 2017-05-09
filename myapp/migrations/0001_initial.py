# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import easymoney
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=60)),
                ('description', models.TextField(max_length=400)),
                ('published_date', models.DateTimeField(null=True, blank=True)),
                ('price', easymoney.MoneyField(default=0, max_digits=12)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
