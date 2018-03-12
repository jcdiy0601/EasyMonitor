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
