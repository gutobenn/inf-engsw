# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_auto_20170510_1343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='price',
            field=models.DecimalField(default=0, verbose_name=b'Pre\xc3\xa7o', max_digits=4, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='rent',
            name='months',
            field=models.PositiveIntegerField(default=1, verbose_name=b'Meses', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(6)]),
        ),
    ]
