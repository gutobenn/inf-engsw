# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_auto_20170510_1342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rent',
            name='months',
            field=models.PositiveIntegerField(verbose_name=b'Meses', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(6)]),
        ),
    ]
