from django import forms
from django.forms import widgets
from django.core.exceptions import ValidationError
from BBS_app import models

class RegForms(forms.Form):
    username = forms.CharField(max_length=10, min_length=3, label='请输入用户名',
                               error_messages={'max_length': '用户名最长为10位', 'min_length': '用户名最短为3位',
                                               'required': '用户名不能为空'},
                               widget=widgets.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(max_length=15, min_length=6, label='请输入密码',
                               error_messages={'max_length': '密码最长为15位', 'min_length': '密码最短为6位',
                                               'required': '密码不能为空'},
                               widget=widgets.PasswordInput(attrs={'class': 'form-control'}))
    re_password = forms.CharField(max_length=15, min_length=6, label='请确认密码',
                                  error_messages={'max_length': '密码最长为15位', 'min_length': '密码最短为6位',
                                                  'required': '密码不能为空'},
                                  widget=widgets.PasswordInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=11, min_length=11, label='请输入手机号',
                            error_messages={'max_length': '手机号必须为11位', 'min_length': '手机号必须为11位',
                                            'required': '手机号不能为空'},
                            widget=widgets.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='请输入邮箱', error_messages={'required': '邮箱不能为空', 'invalid': '不符合邮箱格式'},
                             widget=widgets.EmailInput(attrs={'class': 'form-control'}))

    # 局部校验钩子函数
    def clean_username(self):
        username = self.cleaned_data.get('username')
        # 去数据库校验
        ret = models.UserInfo.objects.filter(username=username).first()
        if ret:
            raise ValidationError('用户名已存在，请重新输入！')
        return username

    # 全局校验钩子函数
    def clean(self):
        password = self.cleaned_data.get('password')
        re_password = self.cleaned_data.get('re_password')
        if password and re_password:
            if password == re_password:
                return self.cleaned_data
            else:
                raise ValidationError('两次密码输入不一致，请重新输入！')
