from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from EasyMonitor import forms


def acclogin(request):
    """用户登录视图"""
    if request.method == 'POST':
        form_obj = forms.AccloginForm(request.POST)     # 表单认证
        if form_obj.is_valid(): # 表单验证成功
            user = authenticate(**form_obj.cleaned_data)    # 用户认证
            if user:    # 用户认证成功
                if user.is_active:  # 用户具有登录权限
                    login(request, user)
                    return redirect('/')
                else:
                    error_message = '该邮箱无权登录'
            else:
                error_message = '用户认证失败,邮箱或密码错误'
        else:
            error_message = '邮箱或密码不能为空'     # 这里格式不对在浏览器提交前就会提示，所以只有空这种可能
        return render(request, 'acclogin.html', {'form_obj': form_obj, 'error_message': error_message})
    form_obj = forms.AccloginForm()
    return render(request, 'acclogin.html', {'form_obj': form_obj})


def acclogout(request):
    """用户登出视图"""
    logout(request)
    return redirect('/login.html')


@login_required
def index(request):
    """首页视图"""
    return render(request, 'index.html')

