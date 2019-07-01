import json

import requests
from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseServerError
import logging, re
from django.contrib.auth import login
from django_redis import get_redis_connection

from carts.utils import merge_cart_cookie_to_redis
from Django_Project.utils import sinaweibopy3
from Django_Project.utils.response_code import RETCODE
from .models import OAuthSinaUser
from .utils import generate_uid_signature, check_uid_signature
from users.models import User


logger = logging.getLogger('django')


# GET /sina/login/?next=xxx
class SinaLoginUrlView(View):
    """提供微博登录页面"""

    def get(self, request):
        """返回微博登录链接login_url"""
        next = request.GET.get("next", "/")

        # 创建微博登录连接对象
        client = sinaweibopy3.APIClient(app_key=settings.SINA_CLIENT_KEY,
                                        app_secret=settings.SINA_CLIENT_SECRET,
                                        redirect_uri=settings.SINA_REDIRECT_URL)

        login_url = client.get_authorize_url()

        return JsonResponse({"code": RETCODE.OK, "message": "OK", "login_url": login_url})


# GET /sina_callback/?code=xxx
class SinaCallbackView(View):
    """提供用户绑定页面"""

    def get(self, request):
        """Oauth2.0认证获取uid"""

        return render(request, 'sina_callback.html')


# GET /oauth/sina/user/?code=xxx
class SinaAuthUserView(View):
    """回调处理"""

    def get(self, request):
        """Oauth2.0认证获取uid"""
        code = request.GET.get("code")

        # 校验参数 判断code有没有过期及伪造的
        if not code:
            return HttpResponseForbidden("缺少参数")

        # 创建微博登录连接对象
        client = sinaweibopy3.APIClient(app_key=settings.SINA_CLIENT_KEY,
                                        app_secret=settings.SINA_CLIENT_SECRET,
                                        redirect_uri=settings.SINA_REDIRECT_URL)

        result = client.request_access_token(code)
        try:
            # 使用code向微博服务器请求access_token
            access_token = result.access_token

            # 使用access_token向微博服务器请求uid
            uid = result.uid
        except Exception as e:
            logger.error(e)
            return HttpResponseServerError("OAuth2.0认证失败")

        try:
            sina_user = OAuthSinaUser.objects.get(uid=uid)

        except OAuthSinaUser.DoesNotExist:
            # 出异常,此用户是新用户,将access_token暂存在html隐藏标签中,并对其进行加密安全处理
            access_token = generate_uid_signature(access_token)
            return JsonResponse({'code': RETCODE.OK, 'message': 'uid未绑定', 'access_token': access_token})

        # 没异常,此用户为老用户,# 直接进行保持状态session
        login(request, sina_user.user)

        token = ''
        # 设置cookie值
        response = JsonResponse({
            'code': RETCODE.OK,
            'message': '已存在用户',
            'user_id': sina_user.user.id,
            'username': sina_user.user.username,
            'token': token
        })

        # 合并购物车
        merge_cart_cookie_to_redis(response=response, request=request)
        response.set_cookie("username", sina_user.user.username, max_age=settings.SESSION_COOKIE_AGE)

        return response

    def post(self, request):
        """微博用户绑定项目用户"""

        # 接受表单参数
        json_dict = json.loads(request.body.decode())

        mobile = json_dict.get("mobile")
        password = json_dict.get("password")
        sms_code_client = json_dict.get("sms_code")
        access_token = json_dict.get("access_token")

        # 校验参数
        if not all([mobile, password, sms_code_client, access_token]):
            return HttpResponseForbidden("缺少必传参数")
        if not re.match(r"^1[3-9]\d{9}$", mobile):
            return HttpResponseForbidden("请输入正确手机号")
        if not re.match(r"^[0-9A-Za-z]{8,20}$", password):
            return HttpResponseForbidden("手机号或密码错误")

        # 创建连接redis数据库对象
        redis_conn = get_redis_connection("verify_code")
        # 从数据库获取短信验证码,以便校验
        sms_code_server = redis_conn.get("sms_%s" % mobile)

        # 判断短信验证码是否过期
        if sms_code_server is None:
            return HttpResponseForbidden("短信验证码过期")

        # 删除数据库中短信验证码,防止频繁发短信验证码
        # redis_conn.delete("sms_%s" % mobile)
        # 将得到的bytes类型的短信验证码转化成字符串,以便比较
        sms_code_server = sms_code_server.decode()

        # 判断短信验证码是否正确
        if sms_code_client != sms_code_server:
            return JsonResponse({"code": RETCODE.SMSCODERR, "message": "短信验证码错误"})

        access_token = check_uid_signature(access_token)
        try:
            response = requests.post('https://api.weibo.com/oauth2/get_token_info',
                                     data=dict(access_token=access_token), verify=False)
            uid = response.json().get('uid')
        except Exception as e:
            logger.error(e)
            return HttpResponseServerError("获取uid失败")

        # 判断当用户是否是已注册用户
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 出异常,创建新用户
            user = User.objects.create_user(username=mobile, password=password, mobile=mobile)
        else:
            # 没有出异常,检验密码对不对
            if not user.check_password(password):
                return JsonResponse({'code': RETCODE.PARAMERR, "message": "用户名或密码错误"}, status=400)
        finally:
            # 绑定uid
            try:
                OAuthSinaUser.objects.create(user=user, uid=uid)
            except OAuthSinaUser.DoesNotExist:
                return HttpResponseServerError("uid无效")

            token = ''
            response = JsonResponse({
                'code': RETCODE.OK,
                'message': '绑定用户成功',
                'token': token,
                'user_id': user.id,
                'username': user.username
            })

            # 状态保持
            login(request, user)

            # 合并购物车
            merge_cart_cookie_to_redis(request=request, response=response)
            response.set_cookie("username", user.username, max_age=settings.SESSION_COOKIE_AGE)

            # 响应
            return response
