from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)


class UserProfileManager(BaseUserManager):
    """用户表管理"""

    def create_user(self, email, name, phone=None, weixin=None, password=None):
        if not email:
            raise ValueError('用户必须有一个email地址')
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            phone=phone,
            weixin=weixin,
        )
        user.set_password(password)
        user.is_active = True
        user.save(using=self.db)
        return user

    def create_superuser(self, email, name, phone=None, weixin=None, password=None):
        user = self.create_user(email, name=name, phone=phone, weixin=weixin, password=password)
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    """用户表"""
    email = models.EmailField(verbose_name='邮箱', max_length=255, unique=True)
    name = models.CharField(verbose_name='姓名', max_length=64)
    phone = models.BigIntegerField(verbose_name='手机号', blank=True, null=True)
    weixin = models.CharField(verbose_name='微信号', max_length=64, blank=True, null=True)
    is_active = models.BooleanField(verbose_name='是否可登录', default=True)
    is_admin = models.BooleanField(verbose_name='是否为管理员', default=False)
    memo = models.TextField(verbose_name='备注', blank=True, null=True)
    date_joined = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = '用户表'
        permissions = (
            ('can_show_user', '可访问用户页面'),
            ('can_show_add_user', '可访问创建用户页面'),
            ('can_add_user', '可创建用户'),
            ('can_del_user', '可删除用户'),
            ('can_show_edit_user', '可访问编辑用户页面'),
            ('can_edit_user', '可编辑用户'),
            ('can_show_change_pass_user', '可访问重置密码页面'),
            ('can_change_pass_user', '可重置密码'),
            ('can_show_change_permission_user', '可访问修改权限页面'),
            ('can_change_permission_user', '可修改权限'),
        )

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.email

    # def has_perm(self, perm, obj=None):
    #     "Does the user have a specific permission?"
    #     # Simplest possible answer: Yes, always
    #     return True
    #
    # def has_module_perms(self, app_label):
    #     "Does the user have permissions to view the app `app_label`?"
    #     # Simplest possible answer: Yes, always
    #     return True

    @property
    def is_staff(self):
        return self.is_admin


class Host(models.Model):
    """主机表"""
    hostname = models.CharField(verbose_name='主机名称', max_length=64, unique=True, help_text='Agent方式要与cmdb客户端配置文件中hostname一致，SNMP、API输入管理IP')
    ip = models.GenericIPAddressField(verbose_name='IP')
    host_groups = models.ManyToManyField(verbose_name='所属主机组', to='HostGroup', blank=True)
    templates = models.ManyToManyField(verbose_name='所属模板', to='Template', blank=True)
    monitor_by_choices = (
        ('agent', '客户端'),
        ('snmp', 'SNMP'),
        ('api', 'API')
    )
    monitor_by = models.CharField(verbose_name='监控方式', max_length=64, choices=monitor_by_choices)
    status_choices = (
        (1, '在线'),
        (2, '宕机'),
        (3, '未知'),
        (4, '下线'),
        (5, '问题')
    )
    status = models.IntegerField(verbose_name='主机状态', choices=status_choices, default=3)
    host_alive_check_interval = models.IntegerField(verbose_name='主机存活状态检测间隔(s)', default=30)
    memo = models.TextField(verbose_name='备注', null=True, blank=True)

    class Meta:
        verbose_name_plural = '主机表'
        permissions = (
            ('can_show_host', '可访问主机页面'),
            ('can_show_add_host', '可访问创建主机页面'),
            ('can_add_host', '可创建主机'),
            ('can_del_host', '可删除主机'),
            ('can_show_edit_host', '可访问编辑主机页面'),
            ('can_edit_host', '可编辑主机'),
        )

    def __str__(self):
        return '%s %s' % (self.hostname, self.ip)


class HostGroup(models.Model):
    """主机组表"""
    name = models.CharField(verbose_name='主机组名称', max_length=64, unique=True)
    templates = models.ManyToManyField(verbose_name='所属模板', to='Template', blank=True)
    memo = models.TextField(verbose_name='备注', null=True, blank=True)

    class Meta:
        verbose_name_plural = '主机组表'
        permissions = (
            ('can_show_host_group', '可访问主机组页面'),
            ('can_show_add_host_group', '可访问创建主机组页面'),
            ('can_add_host_group', '可创建主机组'),
            ('can_del_host_group', '可删除主机组'),
            ('can_show_edit_host_group', '可访问编辑主机组页面'),
            ('can_edit_host_group', '可编辑主机组'),
        )

    def __str__(self):
        return self.name


class Application(models.Model):
    """应用集"""
    name = models.CharField(verbose_name='应用集名称', max_length=64, unique=True)
    plugin_name = models.CharField(verbose_name='插件名称', max_length=64, null=True, blank=True)
    interval = models.IntegerField(verbose_name='监控间隔', default=60)
    items = models.ManyToManyField(verbose_name='所属监控项', to='Item', blank=True)
    memo = models.TextField(verbose_name='备注', null=True, blank=True)

    class Meta:
        verbose_name_plural = '应用集表'
        permissions = (
            ('can_show_application', '可访问应用集页面'),
            ('can_show_add_application', '可访问创建应用集页面'),
            ('can_add_application', '可创建应用集'),
            ('can_del_application', '可删除应用集'),
            ('can_show_edit_application', '可访问编辑应用集页面'),
            ('can_edit_application', '可编辑应用集'),
        )

    def __str__(self):
        return self.name


class Item(models.Model):
    """监控项"""
    name = models.CharField(verbose_name='监控项名称', max_length=64)
    key = models.CharField(verbose_name='键值', max_length=64, unique=True)
    data_type_choices = (
        ('int', '整数'),
        ('float', '小数'),
    )
    data_type = models.CharField(verbose_name='数据类型', max_length=64, choices=data_type_choices)
    data_unit_choices = (
        ('', '无'),
        ('KB', 'KB'),
        ('MB', 'MB'),
        ('GB', 'GB'),
        ('%', '百分比'),
        ('KB/s', 'KB/s'),
        ('MB/s', 'MB/s'),
    )
    data_unit = models.CharField(verbose_name='数据单位', max_length=64, choices=data_unit_choices, null=True, blank=True)
    memo = models.TextField(verbose_name='备注', null=True, blank=True)

    class Meta:
        verbose_name_plural = '监控项表'
        permissions = (
            ('can_show_item', '可访问监控项页面'),
            ('can_show_add_item', '可访问创建监控项页面'),
            ('can_add_item', '可创建监控项'),
            ('can_del_item', '可删除监控项'),
            ('can_show_edit_item', '可访问编辑监控项页面'),
            ('can_edit_item', '可编辑监控项'),
        )

    def __str__(self):
        return '%s %s' % (self.name, self.key)


class Template(models.Model):
    """模板表"""
    name = models.CharField(verbose_name='模板名称', max_length=64, unique=True)
    applications = models.ManyToManyField(verbose_name='所属应用集', to='Application', blank=True)
    memo = models.TextField(verbose_name='备注', null=True, blank=True)

    class Meta:
        verbose_name_plural = '模板表'
        permissions = (
            ('can_show_template', '可访问模板页面'),
            ('can_show_add_template', '可访问创建模板页面'),
            ('can_add_template', '可创建模板'),
            ('can_del_template', '可删除模板'),
            ('can_show_edit_template', '可访问编辑模板页面'),
            ('can_edit_template', '可编辑模板'),
        )

    def __str__(self):
        return self.name


class Trigger(models.Model):
    """触发器表"""
    name = models.CharField(verbose_name='触发器名称', max_length=64)
    templates = models.ForeignKey(verbose_name='所属模板', to='Template')
    severity_choices = (
        ('information', '信息'),
        ('warning', '警告'),
        ('general', '一般严重'),
        ('high', '严重'),
        ('disaster', '灾难')
    )
    severity = models.CharField(verbose_name='报警级别', max_length=64, choices=severity_choices)
    enabled = models.BooleanField(verbose_name='是否启用', default=False)
    memo = models.TextField(verbose_name='备注', null=True, blank=True)

    class Meta:
        verbose_name_plural = '触发器表'
        permissions = (
            ('can_show_trigger', '可访问触发器页面'),
            ('can_show_add_trigger', '可访问创建触发器页面'),
            ('can_add_trigger', '可创建触发器'),
            ('can_del_trigger', '可删除触发器'),
            ('can_show_edit_trigger', '可访问编辑触发器页面'),
            ('can_edit_trigger', '可编辑触发器'),
        )

    def __str__(self):
        return self.name


class TriggerExpression(models.Model):
    """触发器表达式"""
    triggers = models.ForeignKey(verbose_name='所属触发器', to='Trigger')
    applications = models.ForeignKey(verbose_name='所属应用集', to='Application')  # 根据触发器对应的模板获取相关应用集
    items = models.ForeignKey(verbose_name='所属监控项', to='Item')  # 根据触发器对应的模板的应用集获取相关的监控项
    specified_item_key = models.CharField(verbose_name='只监控专门指定的指标key', max_length=64, blank=True, null=True)     # 例如eth0
    operator_choices = (
        ('eq', '='),
        ('lt', '<'),
        ('gt', '>')
    )
    operator = models.CharField(verbose_name='运算符', max_length=64, choices=operator_choices)
    threshold = models.IntegerField(verbose_name='阈值')  # 字符串判断时可规定0或1来判断
    logic_with_next_choices = (
        ('or', 'OR'),
        ('and', 'AND')
    )
    logic_with_next = models.CharField(verbose_name='与一个条件的逻辑关系', max_length=64, choices=logic_with_next_choices, null=True, blank=True)
    data_calc_func_choices = (
        ('avg', '平均值'),
        ('last', '最近的值'),
    )
    data_calc_func = models.CharField(verbose_name='数据运算函数', max_length=64, choices=data_calc_func_choices)
    data_calc_func_args = models.CharField(verbose_name='数据运算函数的非固定参数,json格式', max_length=64, help_text='如：{"time": 5}，表示5分钟', null=True, blank=True)
    memo = models.TextField(verbose_name='备注', null=True, blank=True)

    class Meta:
        verbose_name_plural = '触发器表达式表'

    def __str__(self):
        return '%s' % self.triggers


class Action(models.Model):
    """报警策略，定义trigger发生后，如何报警"""
    name = models.CharField(verbose_name='报警策略名称', max_length=64, unique=True)
    triggers = models.ManyToManyField(verbose_name='所属触发器', to='Trigger')
    interval = models.IntegerField(verbose_name='报警间隔(s)', default=300)
    _alert_msg_format = '''主机:{hostname}
IP:{ip}
应用集:{name}
内容:{msg},存在问题
开始时间:{start_time}
持续时间:{duration}'''
    alert_msg_format = models.TextField(verbose_name='报警通知格式', default=_alert_msg_format)
    recover_notice = models.BooleanField(verbose_name='故障恢复后是否发送通知', default=False)
    _recover_msg_format = '''主机:{hostname}
IP:{ip}
应用集:{name}
内容:{msg},问题恢复
开始时间:{start_time}
持续时间:{duration}
恢复时间:{recover_time}'''
    recover_msg_format = models.TextField(verbose_name='恢复通知格式', default=_recover_msg_format)
    action_operations = models.ManyToManyField(verbose_name='所属报警动作', to='ActionOperation')
    enabled = models.BooleanField(verbose_name='是否启用', default=False)
    memo = models.TextField(verbose_name='备注', null=True, blank=True)

    class Meta:
        verbose_name_plural = '报警策略表'
        permissions = (
            ('can_show_action', '可访问报警策略页面'),
            ('can_show_add_action', '可访问创建报警策略页面'),
            ('can_add_action', '可创建报警策略'),
            ('can_del_action', '可删除报警策略'),
            ('can_show_edit_action', '可访问编辑报警策略页面'),
            ('can_edit_action', '可编辑报警策略'),
        )

    def __str__(self):
        return self.name


class ActionOperation(models.Model):
    """报警动作"""
    name = models.CharField(verbose_name='报警动作名称', max_length=64, unique=True)
    action_type_choices = (
        ('email', '邮件'),
        ('sms', '短信'),
        ('weixin', '微信'),
        ('script', '脚本')
    )
    action_type = models.CharField(verbose_name='动作类型', max_length=64, choices=action_type_choices)
    step = models.IntegerField(verbose_name='报警升级阈值')
    user_profiles = models.ManyToManyField(verbose_name='所属用户', to='UserProfile', blank=True)
    script_name = models.CharField(verbose_name='脚本名称', max_length=64, null=True, blank=True)
    memo = models.TextField(verbose_name='备注', null=True, blank=True)

    class Meta:
        verbose_name_plural = '报警动作表'
        permissions = (
            ('can_show_action_operation', '可访问报警动作页面'),
            ('can_show_add_action_operation', '可访问创建报警动作页面'),
            ('can_add_action_operation', '可创建报警动作'),
            ('can_del_action_operation', '可删除报警动作'),
            ('can_show_edit_action_operation', '可访问编辑报警动作页面'),
            ('can_edit_action_operation', '可编辑报警动作'),
        )

    def __str__(self):
        return self.name


class Chart(models.Model):
    """图表"""
    name = models.CharField(verbose_name='图表名称', max_length=64, unique=True)
    chart_type_choices = (
        ('line', '线型图'),
        ('area', '面积图'),
        ('pie', '饼图'),
    )
    chart_type = models.CharField(verbose_name='图表类型', max_length=64, choices=chart_type_choices)
    templates = models.ForeignKey(verbose_name='所属模板', to='Template')
    applications = models.ForeignKey(verbose_name='所属应用集', to='Application')
    items = models.ManyToManyField(verbose_name='所属监控项', to='Item')
    auto = models.BooleanField(verbose_name='是否自动', default=False)
    memo = models.TextField(verbose_name='备注', null=True, blank=True)

    class Meta:
        verbose_name_plural = '图表'
        permissions = (
            ('can_show_chart', '可访问图表页面'),
            ('can_show_add_chart', '可访问创建图表页面'),
            ('can_add_chart', '可创建图表'),
            ('can_del_chart', '可删除图表'),
            ('can_show_edit_chart', '可访问编辑图表页面'),
            ('can_edit_chart', '可编辑图表'),
        )

    def __str__(self):
        return self.name


class EventLog(models.Model):
    """存储报警及其他事件日志"""
    event_type_choices = (
        (0, '报警事件'),
        (1, '维护事件')
    )
    event_type = models.IntegerField(verbose_name='事件类型', choices=event_type_choices)
    hosts = models.ForeignKey(verbose_name='所属主机', to='Host')
    triggers = models.ForeignKey(verbose_name='所属触发器', to='Trigger', null=True, blank=True)
    log = models.TextField(verbose_name='日志', null=True, blank=True)
    date = models.DateTimeField(verbose_name='日期', auto_now_add=True)
    memo = models.TextField(verbose_name='备注', null=True, blank=True)

    class Meta:
        verbose_name_plural = '事件日志表'

    def __str__(self):
        return '%s %s' % (self.hosts, self.log)
