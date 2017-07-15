# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-15 03:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alugueme', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rent',
            name='due_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='rent',
            name='status',
            field=models.IntegerField(choices=[(1, b'Pendente'), (2, b'Cancelado'), (3, b'Confirmado'), (4, b'Encerrado'), (5, b'Atrasado')], default=1),
        ),
    ]
