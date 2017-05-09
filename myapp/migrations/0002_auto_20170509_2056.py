# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import easymoney


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, b'Available'), (2, b'Unavailable')]),
        ),
        migrations.AlterField(
            model_name='item',
            name='description',
            field=models.TextField(max_length=800, verbose_name=b'Descri\xc3\xa7\xc3\xa3o'),
        ),
        migrations.AlterField(
            model_name='item',
            name='price',
            field=easymoney.MoneyField(default=0, verbose_name=b'Pre\xc3\xa7o', max_digits=12),
        ),
        migrations.AlterField(
            model_name='item',
            name='title',
            field=models.CharField(max_length=60, verbose_name=b'T\xc3\xadtulo'),
        ),
    ]
