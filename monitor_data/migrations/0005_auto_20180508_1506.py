# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-05-08 07:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor_data', '0004_auto_20180508_1448'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actionoperation',
            name='msg_format',
            field=models.TextField(default='主机:{hostname}\nIP:{ip}\n应用集:{name},存在问题\n内容:{msg}', verbose_name='消息格式'),
        ),
    ]
