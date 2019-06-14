import logging
import re
from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.contrib.auth import login, authenticate, logout, mixins
from django_redis import get_redis_connection

from Django_Project.utils.response_code import RETCODE, err_msg
from .models import User


logger = logging.getLogger('django')  # 创建日志输出器对象


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
        query_dict = request.POST  # 表单查询字典
        username = query_dict.get('username')
        password = query_dict.get('password')
        password2 = query_dict.get('password2')
        mobile = query_dict.get('mobile')
        sms_code_client = query_dict.get('sms_code')
        allow = query_dict.get('allow')  # on或None

        """
        此处校验的参数，前端已经校验过，如果参数还是出错，
        说明该请求是非正常渠道发送的，直接通过HttpResponseForbidden禁止本次请求
        """
        if not all([username, password, password2, mobile, allow]):  # 表单值没有(None)或者为空("",{},(),[])
            return HttpResponseForbidden("缺少必传参数")  # 403
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

        redis_conn = get_redis_connection('verify_code')
        # 获取redis中的短信验证码
        sms_code_server = redis_conn.get('sms_%s' % mobile)

        if sms_code_server is None:
            data = {
                'sms_code_errmsg': '无效的短信验证码'
            }
            return JsonResponse(data)

        redis_conn.delete('sms_%s' % mobile)

        if sms_code_server.decode() != sms_code_client:
            data = {
                'sms_code_errmsg': '短信验证码有误'
            }
            return JsonResponse(data)

        # 新建用户，保存注册数据
        try:
            """
            create_user方法可以将password进行加密保存:
                user = set_password(password)
                user.save()
            """
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError as e:
            logger.error(e)
            return render(request, 'register.html', context={'register_errmsg': '注册失败'})

        # 登入用户，实现状态保持
        login(request, user)  # 存储用户的id到session中记录它的登录状态
        response = redirect('contents:index')  # 创建响应对象

        # 注册成功 用户名写入到cookie，有效期两周
        response.set_cookie('username', user.username, max_age=3600 * 24 * 14)
        # merge_cart_cookie_to_redis(request, response)

        # 注册成功则重定向到index首页
        return response


# 通过axios发送GET请求 /usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/
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
            'code': RETCODE.OK,  # 自定义的状态码
            'errmsg': err_msg[RETCODE.OK],
            'count': count
        }
        return JsonResponse(data)


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
            'code': RETCODE.OK,
            'errmsg': err_msg[RETCODE.OK],
            'count': count
        }
        return JsonResponse(data)


class LoginView(View):
    """用户名登录"""

    def get(self, request):
        """
        提供注册页面
        :param request: 请求对象
        :return: 渲染登录界面
        """
        return render(request, 'login.html')

    def post(self, request):
        """
        实现登录逻辑
        :param request:
        :return: 登录结果
        """
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        # django自带认证登录用户
        user = authenticate(request, username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})

        # 实现状态保持
        login(request, user)
        # 设置状态保持时长
        if remembered is None:
            # 如果没有勾选记住登录，session会话在浏览器关闭就结束
            # 默认为两周，设置为None表示默认
            request.session.set_expiry(0)

        response = redirect(reverse('contents:index'))  # 登录成功重定向到首页
        # 登录成功 用户名写入到cookie，有效期两周(前端获取到用于展示用户信息)
        # None表示在浏览器关闭就清除，0表示刚生成就清除了
        response.set_cookie('username', user.username, max_age=3600 * 24 * 14)

        return response
