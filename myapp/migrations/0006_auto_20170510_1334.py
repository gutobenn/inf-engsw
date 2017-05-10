# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('myapp', '0005_auto_20170509_2244'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=1, choices=[(1, b'Pendente'), (2, b'Cancelado'), (3, b'Confirmado')])),
                ('request_date', models.DateTimeField()),
                ('confirmation_date', models.DateTimeField(null=True, blank=True)),
                ('months', models.IntegerField()),
                ('payment', models.IntegerField(choices=[(1, b'Dinheiro'), (2, b'Troca')])),
            ],
        ),
        migrations.AlterField(
            model_name='item',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, b'Dispon\xc3\xadvel'), (2, b'Indispon\xc3\xadvel')]),
        ),
        migrations.AddField(
            model_name='rent',
            name='item',
            field=models.OneToOneField(to='myapp.Item'),
        ),
        migrations.AddField(
            model_name='rent',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
    ]
