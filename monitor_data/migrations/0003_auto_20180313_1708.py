# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-03-13 09:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor_data', '0002_auto_20180313_1656'),
    ]

    operations = [
        migrations.AlterField(
            model_name='items',
            name='name',
            field=models.CharField(max_length=64, verbose_name='监控项名称'),
        ),
    ]
