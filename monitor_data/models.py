from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)


class UserProfileManager(BaseUserManager):
    """用户表管理"""
    def create_user(self, email, name, phone=None, weixin=None,  password=None):
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
    memo = models.TextField(verbose_name='备注', blank=True, null=True, default=None)
    date_joined = models.DateTimeField(verbose_name='创建时间', blank=True, null=True, auto_now_add=True)

    class Meta:
        verbose_name_plural = '用户表'

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
    hostname = models.CharField(verbose_name='主机名称', max_length=64, unique=True, help_text='agen输入cmdb客户端配置文件中hostname，snmp输入管理IP')
    ip = models.GenericIPAddressField(verbose_name='IP')
    host_groups = models.ManyToManyField(verbose_name='所属主机组', to='HostGroup', blank=True)
    templates = models.ManyToManyField(verbose_name='所属模板', to='Template', blank=True)
    monitor_by_choices = (
        ('agent', '客户端'),
        ('snmp', 'SNMP')
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
    host_alive_check_interval = models.IntegerField(verbose_name='主机存活状态检测间隔', default=30)
    memo = models.TextField(verbose_name='备注', null=True, blank=True)

    class Meta:
        verbose_name_plural = '主机表'

    def __str__(self):
        return '%s<%s>' % (self.hostname, self.ip)


class HostGroup(models.Model):
    """主机组表"""
    name = models.CharField(verbose_name='主机组名称', max_length=64, unique=True)
    templates = models.ManyToManyField(verbose_name='所属模板', to='Template')
    memo = models.TextField(verbose_name='备注', null=True, blank=True)

    class Meta:
        verbose_name_plural = '主机组表'

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

    def __str__(self):
        return self.name


class Item(models.Model):
    """监控项"""
    name = models.CharField(verbose_name='监控项名称', max_length=64)
    key = models.CharField(verbose_name='键值', max_length=64, unique=True)
    data_type_choices = (
        ('int', '整数'),
        ('float', '小数'),
        ('str', '字符串'),
    )
    data_type = models.CharField(verbose_name='数据类型', max_length=64, choices=data_type_choices)
    unit = models.CharField(verbose_name='数据单位', max_length=64, null=True, blank=True)
    memo = models.TextField(verbose_name='备注', null=True, blank=True)

    class Meta:
        verbose_name_plural = '监控项表'

    def __str__(self):
        return '%s<%s>' % (self.name, self.key)


class Template(models.Model):
    """模板表"""
    name = models.CharField(verbose_name='模板名称', max_length=64, unique=True)
    applications = models.ManyToManyField(verbose_name='所属应用集', to='Application', blank=True)
    memo = models.TextField(verbose_name='备注', null=True, blank=True)

    class Meta:
        verbose_name_plural = '模板表'

    def __str__(self):
        return self.name


class Trigger(models.Model):
    """触发器表"""
    name = models.CharField(verbose_name='触发器名称', max_length=64, null=True, blank=True)
    templates = models.ForeignKey(verbose_name='所属模板', to='Template')
    severity_choices = (
        ('information', '信息'),
        ('warning', '警告'),
        ('general', '一般严重'),
        ('high', '严重'),
        ('disaster', '灾难')
    )
    severity = models.CharField(verbose_name='报警级别', max_length=64, choices=severity_choices)
    enabled = models.BooleanField(verbose_name='是否启用', default=True)
    memo = models.TextField(verbose_name='备注', null=True, blank=True)

    class Meta:
        verbose_name_plural = '触发器表'

    def __str__(self):
        return self.name


class TriggerExpression(models.Model):
    """触发器表达式"""
    triggers = models.ForeignKey(verbose_name='所属触发器', to='Trigger')
    applications = models.ForeignKey(verbose_name='所属应用集', to='Application')   # 根据触发器对应的模板获取相关应用集
    items = models.ForeignKey(verbose_name='所属监控项', to='Item')     # 根据触发器对应的模板的应用集获取相关的监控项
    operator_choices = (
        ('eq', '='),
        ('lt', '<'),
        ('gt', '>')
    )
    operator = models.CharField(verbose_name='运算符', max_length=64, choices=operator_choices)
    threshold = models.IntegerField(verbose_name='阈值')  # 字符串判断时可规定0或1来判断
    logic_choices = (
        ('or', 'OR'),
        ('and', 'AND')
    )
    logic_with_next = models.CharField(verbose_name='与一个条件的逻辑关系', max_length=64, choices=logic_choices, null=True, blank=True)
    data_calc_func_choices = (
        ('avg', '平均值'),
        ('max', '最大值'),
        ('min', '最小值'),
        ('hit', 'HIT'),
        ('last', '最近的值'),
    )
    data_calc_func = models.CharField(verbose_name='数据运算函数', max_length=64, choices=data_calc_func_choices, default='last')
    data_calc_func_args = models.CharField(verbose_name='数据运算函数的非固定参数,json格式', max_length=64, null=True, blank=True)
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
    recover_notice = models.BooleanField(verbose_name='故障恢复后是否发送通知', default=True)
    recover_subject = models.CharField(verbose_name='恢复通知主题', max_length=128, null=True, blank=True)
    recover_message = models.TextField(verbose_name='恢复通知内容', null=True, blank=True)
    actionoperations = models.ManyToManyField(verbose_name='所属报警动作', to='ActionOperation')
    enabled = models.BooleanField(verbose_name='是否启用', default=True)
    memo = models.TextField(verbose_name='备注', null=True, blank=True)

    class Meta:
        verbose_name_plural = '报警策略表'

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
    action_type = models.CharField(verbose_name='动作类型', max_length=64, choices=action_type_choices, default='email')
    step = models.IntegerField(verbose_name='报警升级阈值')
    userprofiles = models.ManyToManyField(verbose_name='所属用户', to='UserProfile', blank=True)
    script_name = models.CharField(verbose_name='脚本名称', max_length=64, null=True, blank=True)
    _msg_format = '''主机({hostname},{ip}) 应用集({name})存在问题,内容:{msg}'''
    msg_format= models.TextField(verbose_name='消息格式', default=_msg_format)
    memo = models.TextField(verbose_name='备注', null=True, blank=True)

    class Meta:
        verbose_name_plural = '报警动作表'

    def __str__(self):
        return self.name
