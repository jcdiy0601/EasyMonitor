# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-06-20 03:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor_data', '0030_chart_specified_item_key'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chart',
            name='specified_item_key',
        ),
        migrations.AddField(
            model_name='chart',
            name='auto',
            field=models.BooleanField(default=False, verbose_name='是否自动'),
        ),
    ]
