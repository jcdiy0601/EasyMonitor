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


class Hosts(models.Model):
    """主机表"""
    ip = models.GenericIPAddressField(verbose_name='IP', unique=True)
    hostname = models.CharField(verbose_name='主机名称', max_length=64, unique=True)
    hosts_groups = models.ManyToManyField(verbose_name='所属主机组', to='HostsGroups', blank=True)
    templates = models.ManyToManyField(verbose_name='所属模板', to='Templates', blank=True)
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
    memo = models.TextField(verbose_name='备注', blank=True, null=True)

    class Meta:
        verbose_name_plural = '主机表'

    def __str__(self):
        return '%s<%s>' % (self.hostname, self.ip)


class HostsGroups(models.Model):
    """主机组表"""
    name = models.CharField(verbose_name='主机组名称', max_length=64, unique=True)
    templates = models.ManyToManyField(verbose_name='所属模板', to='Templates')
    memo = models.TextField(verbose_name='备注', blank=True, null=True)

    class Meta:
        verbose_name_plural = '主机组表'

    def __str__(self):
        return self.name


class Applications(models.Model):
    """应用集"""
    name = models.CharField(verbose_name='应用集名称', max_length=64, unique=True)
    plugin_name = models.CharField(verbose_name='插件名称', max_length=64, null=True, blank=True)
    interval = models.IntegerField(verbose_name='监控间隔', default=60)
    items = models.ManyToManyField(verbose_name='所属监控项', to='Items', blank=True)
    memo = models.TextField(verbose_name='备注', blank=True, null=True)

    class Meta:
        verbose_name_plural = '应用集表'

    def __str__(self):
        return self.name


class Items(models.Model):
    """监控项"""
    name = models.CharField(verbose_name='监控项名称', max_length=64)
    key = models.CharField(verbose_name='键值', max_length=64, unique=True)
    data_type_choices = (
        ('int', '整数'),
        ('float', '小数'),
        ('str', '字符串'),
    )
    data_type = models.CharField(verbose_name='数据类型', max_length=64, choices=data_type_choices)
    memo = models.TextField(verbose_name='备注', blank=True, null=True)

    class Meta:
        verbose_name_plural = '监控项表'

    def __str__(self):
        return '%s<%s>' % (self.name, self.key)


class Templates(models.Model):
    """模板表"""
    name = models.CharField(verbose_name='模板名称', max_length=64, unique=True)
    applications = models.ManyToManyField(verbose_name='所属应用集', to='Applications', blank=True)

    class Meta:
        verbose_name_plural = '模板表'

    def __str__(self):
        return self.name

