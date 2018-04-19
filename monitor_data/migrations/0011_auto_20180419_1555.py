# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-04-19 07:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('monitor_data', '0010_auto_20180418_1756'),
    ]

    operations = [
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hostname',
                 models.CharField(help_text='agen输入cmdb客户端配置文件中hostname，snmp输入管理IP', max_length=64, unique=True,
                                  verbose_name='主机名称')),
                ('ip', models.GenericIPAddressField(verbose_name='IP')),
                ('monitor_by',
                 models.CharField(choices=[('agent', '客户端'), ('snmp', 'SNMP')], max_length=64, verbose_name='监控方式')),
                ('status',
                 models.IntegerField(choices=[(1, '在线'), (2, '宕机'), (3, '未知'), (4, '下线'), (5, '问题')], default=3,
                                     verbose_name='主机状态')),
                ('host_alive_check_interval', models.IntegerField(default=30, verbose_name='主机存活状态检测间隔')),
                ('memo', models.TextField(blank=True, null=True, verbose_name='备注')),
            ],
            options={
                'verbose_name_plural': '主机表',
            },
        ),
        migrations.RenameModel(
            old_name='Applications',
            new_name='Application',
        ),
        migrations.RenameModel(
            old_name='HostsGroups',
            new_name='HostGroup',
        ),
        migrations.RenameModel(
            old_name='Items',
            new_name='Item',
        ),
        migrations.RenameModel(
            old_name='Templates',
            new_name='Template',
        ),
        migrations.RemoveField(
            model_name='hosts',
            name='hosts_groups',
        ),
        migrations.RemoveField(
            model_name='hosts',
            name='templates',
        ),
        migrations.RenameField(
            model_name='action',
            old_name='operations',
            new_name='actionoperations',
        ),
        migrations.RenameField(
            model_name='actionoperation',
            old_name='notifiers',
            new_name='userprofiles',
        ),
        migrations.RenameField(
            model_name='trigger',
            old_name='template',
            new_name='templates',
        ),
        migrations.RenameField(
            model_name='triggerexpression',
            old_name='trigger',
            new_name='triggers',
        ),
        migrations.DeleteModel(
            name='Hosts',
        ),
        migrations.AddField(
            model_name='host',
            name='host_groups',
            field=models.ManyToManyField(blank=True, to='monitor_data.HostGroup', verbose_name='所属主机组'),
        ),
        migrations.AddField(
            model_name='host',
            name='templates',
            field=models.ManyToManyField(blank=True, to='monitor_data.Template', verbose_name='所属模板'),
        ),
    ]
