import re
from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import login

from .models import User


# /mobiles/(?P<mobile>1[3-9]\d{9})/count/
class MobileCountView(View):
    """判断手机号是否重复注册"""

    def get(self, request, mobile):
        """
        :param request: 请求对象
        :param mobile: 手机号
        :return: JSON
        """
        count = User.objects.filter(mobile=mobile).count()
        data = {
            'code': 200,
            'errmsg': 'OK',
            'count': count
        }
        return HttpResponse(data)


# /usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/
class UsernameCountView(View):
    """判断用户名是否重复注册"""

    def get(self, request, username):
        """
        :param request: 请求对象
        :param username: 用户注册时输入的用户名
        :return: JSON
        """
        count = User.objects.filter(username=username).count()
        data = {
            'code': 200,
            'errmsg': 'OK',
            'count': count
        }
        return HttpResponse(data)


# GET&POST register/
class RegisterView(View):
    """用户注册"""

    def get(self, request):
        """
        提供注册页面
        :param request: 请求对象
        :return: 渲染回注册页面模板
        """
        return render(request, 'register.html')

    def post(self, request):
        """
        实现用户注册
        :param request: 请求对象
        :return: 注册结果
        """
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')

        """
        此处校验的参数，前端已经校验过，如果参数还是出错，
        说明该请求是非正常渠道发送的，直接通过HttpResponseForbidden禁止本次请求
        """
        if not all([username, password, password2, mobile, allow]):
            return HttpResponseForbidden("缺少必传参数")
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return HttpResponseForbidden("请输入5-20个字符的用户名")
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseForbidden("请输入8-20位的密码")
        if password2 != password:
            return HttpResponseForbidden("两次输入的密码不一致")
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseForbidden("请输入正确的手机号码")
        if allow != "on":
            return HttpResponseForbidden("请勾选用户协议")

        # 新建用户，保存注册数据
        try:
            user = User.objects.create(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', context={'register_errmsg': '注册失败'})

        # 登入用户，实现状态保持
        login(request, user)

        # 注册成功则重定向到index首页
        return redirect(reverse('contents:index'))
