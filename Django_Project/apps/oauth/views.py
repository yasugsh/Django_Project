from django.shortcuts import render, redirect
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseServerError
import logging
from django.contrib.auth import login
import re
from django_redis import get_redis_connection
from django.db import DatabaseError

from Django_Project.utils.response_code import RETCODE, err_msg
from .models import OAuthQQUser
from .utils import generate_openid_signature, check_openid_signature
from users.models import User


logger = logging.getLogger('django')


class QQAuthURLView(View):
    """提供QQ登录页面网址
    https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=xxx&redirect_uri=xxx&state=xxx
    """

    # qq/authorization/?next=xxx
    def get(self, request):
        # next表示从哪个页面进入登录页面
        next = request.GET.get('next', '/')

        # 初始化OAuthQQ工具类对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=next)
        qq_login_url = oauth.get_qq_url()

        data = {
            'code': RETCODE.OK,
            'errmsg': 'OK',
            'login_url': qq_login_url
        }
        """
        from urllib.parse import urlencode
        # 生成GET请求参数:
        # query_params = urlencode(data)
        #   query_params --> 'code=RETCODE.OK&errmsg=OK&login_url=qq_login_url'
        """
        return JsonResponse(data)


class QQAuthUserView(View):
    """用户扫码登录后的回调处理
    http://www.meiduo.site:8000/oauth_callback/?code=AE263F12675FA79185B54870D79730A7&state=%2F
    """

    # oauth_callback/?code=xxx&state=xxx
    def get(self, request):
        """OAuth2.0认证"""
        # 接收QQ扫码后生成的Authorization Code
        code = request.GET.get('code')
        if not code:
            return HttpResponseForbidden('缺少code')

        # 初始化OAuthQQ工具类对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)
        try:
            # 使用Authorization Code向QQ服务器请求access_token
            access_token = oauth.get_access_token(code)

            # 使用access_token向QQ服务器请求openid
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            logger.error(e)
            return HttpResponseServerError('OAuth2.0认证失败')

        try:
            # 使用扫码QQ的openid查询QQ用户
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 如果没查到用户，表示扫码QQ未绑定过用户
            # 将openid加密后响应给前端，用于后续绑定用户
            token_openid = generate_openid_signature(openid)
            context = {'openid': token_openid}
            return render(request, 'oauth_callback.html', context)

        # 如果查到用户，表示扫码的QQ有绑定过用户
        # 获取到绑定的用户，直接进行登录并状态保持
        qq_user = oauth_user.user
        login(request, qq_user)

        next = request.GET.get('state', '/')
        response = redirect(next)
        response.set_cookie('username', qq_user.username, max_age=settings.SESSION_COOKIE_AGE)
        return response

    def post(self, request):
        """openid绑定到用户"""

        # 接收参数
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        sms_code_client = request.POST.get('sms_code')
        token_openid = request.POST.get('openid')

        if not all([mobile, password, sms_code_client]):
            return HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseForbidden('请输入正确的手机号码')
        if not re.match(r'^[0-9a-zA-Z]{8,20}$', password):
            return HttpResponseForbidden('请输入8-20位的密码')

        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '无效的短信验证码'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '输入短信验证码有误'})

        openid = check_openid_signature(token_openid)
        # 判断openid是否有效，错误提示放在openid_errmsg位置
        if not openid:
            return render(request, 'oauth_callback.html', {'openid_errmsg': '无效的openid'})

        # 使用mobile获取用户对象
        try:
            # 根据电话号码查询user对象
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # user不存在，新建用户
            user = User.objects.create_user(username=mobile, password=password, mobile=mobile)
        else:
            # user存在，检查用户密码
            if not user.check_password(password):
                return render(request, 'oauth_callback.html', {'account_errmsg': '用户名或密码错误'})

        # 创建QQ登录用户对象并绑定user对象
        try:
            # 直接将加密的openid存到数据库
            OAuthQQUser.objects.create(openid=openid, user=user)
        except DatabaseError:
            return render(request, 'oauth_callback.html', {'qq_login_errmsg': 'QQ登录失败'})

        login(request, user)

        next = request.GET.get('state', '/')
        response = redirect(next)
        response.set_cookie('username', user.username, max_age=settings.SESSION_COOKIE_AGE)
        return response
