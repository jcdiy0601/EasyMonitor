# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-05-10 02:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor_data', '0008_auto_20180509_1524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='data_type',
            field=models.CharField(choices=[('int', '整数'), ('float', '小数')], max_length=64, verbose_name='数据类型'),
        ),
    ]