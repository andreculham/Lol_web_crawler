# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-03-20 21:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20180321_0302'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='league',
            field=models.CharField(default=0, max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='match',
            name='region',
            field=models.CharField(default=0, max_length=200),
            preserve_default=False,
        ),
    ]
