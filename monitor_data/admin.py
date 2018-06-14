from django.contrib import admin
from django import forms
from monitor_data import models
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = models.UserProfile
        fields = ('email', 'name', 'phone', 'weixin')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = models.UserProfile
        fields = ('email', 'password', 'name', 'phone', 'weixin', 'is_active', 'is_admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserProfileAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'name', 'phone', 'weixin', 'is_active', 'is_admin')  # 列表页表格显示的字段
    list_filter = ('is_admin',)  # 列表页可以过滤的字段
    fieldsets = (  # 信息页显示
        ('账号信息', {'fields': ('email', 'password')}),
        ('个人信息', {'fields': ('name', 'phone', 'weixin')}),
        ('权限', {'fields': ('is_active', 'is_admin', 'user_permissions', 'groups')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        ('创建账号', {
            'classes': ('wide',),
            'fields': ('email', 'name', 'phone', 'weixin', 'password1', 'password2', 'is_active', 'is_admin')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('user_permissions', 'groups')


# Now register the new UserAdmin...
admin.site.register(models.UserProfile, UserProfileAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)


class TriggerExpressionInline(admin.TabularInline):
    model = models.TriggerExpression


class TriggerAdmin(admin.ModelAdmin):
    list_display = ('name', 'severity', 'enabled')
    inlines = [TriggerExpressionInline, ]


admin.site.register(models.Host)
admin.site.register(models.HostGroup)
admin.site.register(models.Application)
admin.site.register(models.Item)
admin.site.register(models.Template)
admin.site.register(models.Trigger, TriggerAdmin)
admin.site.register(models.TriggerExpression)
admin.site.register(models.Action)
admin.site.register(models.ActionOperation)
admin.site.register(models.Chart)
admin.site.register(models.EventLog)
