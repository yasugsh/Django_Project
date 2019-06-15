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
            # 使用此openid查询QQ用户
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 如果没查到用户，表示扫码QQ未绑定过用户
            # 将openid加密处理后响应给前端，用于后续绑定用户
            token_openid = generate_openid_signature(openid)
            context = {'openid': token_openid}
            return render(request, 'oauth_callback.html', context)
        pass
