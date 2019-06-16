import logging
import re
from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse, HttpResponseServerError
from django.contrib.auth import login, authenticate, logout, mixins
from django_redis import get_redis_connection
from django.conf import settings
from django.contrib.auth.decorators import login_required
import json

from Django_Project.utils.response_code import RETCODE, err_msg
from .models import User
from celery_tasks.email.tasks import send_verify_email
from .utils import generate_verify_email_url, check_verify_email_token
from .models import Address
from users import constants


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

        # 注册成功 用户名写入到cookie，设置有效期与session一致(两周)
        response.set_cookie('username', user.username, max_age=settings.SESSION_COOKIE_AGE)
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

        next = request.GET.get('next', '/')
        response = redirect(next)  # 登录成功重定向到next页或首页

        # 登录成功 用户名写入到cookie，有效期两周(前端获取到用于展示用户信息)
        # None表示在浏览器关闭就清除，0表示刚生成就清除了
        response.set_cookie('username', user.username, max_age=settings.SESSION_COOKIE_AGE if remembered else None)

        return response


class LogoutView(View):
    """退出登录"""

    def get(self, request):
        # 清除session
        logout(request)
        # 退出登录后重定向到登录页,并清除cookie中的username
        response = redirect(reverse('users:login'))
        response.delete_cookie('username')

        return response


class UserInfoView(mixins.LoginRequiredMixin, View):
    """用户中心"""

    def get(self, request):
        """提供个人信息界面"""

        # 方式1、if判断用户是否登录
        # if request.user.is_authenticated():
        #     # 当前用户已经登录才展示用户中心
        #     return render(request, 'user_center_info.html')
        # else:
        #     # 用户未登录重定向到登录页面
        #     return redirect('/login/?next=/info/')

        # 方式2、url中利用login_required装饰器判断用户是否登录
        # 方式3、通过继承LoginRequiredMixin判断用户是否登录
        context = {
            "username": request.user.username,
            "mobile": request.user.mobile,
            "email": request.user.email,
            "email_active": request.user.email_active
        }
        return render(request, 'user_center_info.html', context)

class EmailView(mixins.LoginRequiredMixin, View):
    """用户添加邮箱"""

    def put(self, request):
        json_dict = json.loads(request.body.decode())
        email = json_dict.get('email')

        if not email:
            return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少email参数'})
        if not re.match(r'^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$', email):
            return JsonResponse({'code': RETCODE.EMAILERR, 'errmsg': 'email格式错误'})

        # 获取当前登录用户
        user = request.user
        try:
            # 修改email
            user.email = email
            user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败'})

        verify_url = generate_verify_email_url(user)
        # 异步任务发送验证邮件
        send_verify_email.delay(email, verify_url)

        # 响应添加邮箱结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})


class VerifyEmailView(View):
    """验证邮箱"""

    def get(self, request):
        # 接收查询参数
        token = request.GET.get('token')
        # 校验参数：判断token是否为空和过期
        if not token:
            return HttpResponseForbidden('缺少token')

        # 提取user
        user = check_verify_email_token(token)
        if not user:
            return HttpResponseForbidden('无效的token')

        # 修改email_active的值为True
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return HttpResponseServerError('激活邮箱失败')
        # 返回邮箱验证结果
        return redirect(reverse('users:info'))


class AddressView(mixins.LoginRequiredMixin, View):
    """用户收货地址"""

    def get(self, request):
        """展示用户所有收货地址"""
        login_user = request.user
        addresses = Address.objects.filter(user=login_user, is_deleted=False)

        address_dict_list = []
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_dict_list.append(address_dict)

        context = {
            'default_address_id': login_user.default_address_id,
            'addresses': address_dict_list
        }

        return render(request, 'user_center_site.html', context)


class CreateAddressView(mixins.LoginRequiredMixin, View):
    """用户新增地址"""

    def post(self, request):
        # 判断是否超过地址上限：最多20个
        # count = Address.objects.filter(user=request.user).count()
        count = request.user.addresses.count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '超过地址数量上限'})

        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')  # 收货人
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')  # 具体地址
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')  # 固定电话
        email = json_dict.get('email')

        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseForbidden('手机号码错误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return HttpResponseForbidden('固定号码错误')
        if email:
            if not re.match(r'^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$', email):
                return HttpResponseForbidden('email有误')

        # 保存地址信息
        try:
            address = Address.objects.create(
                user = request.user,
                title = receiver,
                receiver = receiver,
                province_id = province_id,
                city_id = city_id,
                district_id = district_id,
                place = place,
                mobile = mobile,
                tel = tel,
                email = email
            )

            # 设置默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})

        # 将新增的地址响应给前端进行局部刷新
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应保存结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})


class UpdateDeleteAddressView(mixins.LoginRequiredMixin, View):
    """修改和删除地址"""

    def put(self, request, address_id):
        """
        修改收货地址
        :param request:
        :param address_id: 要修改的地址ID（路径参数）
        :return: json
        """
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')  # 收货人
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')  # 具体地址
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')  # 固定电话
        email = json_dict.get('email')

        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseForbidden('手机号码错误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return HttpResponseForbidden('固定号码错误')
        if email:
            if not re.match(r'^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$', email):
                return HttpResponseForbidden('email有误')

        try:
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '修改收货地址失败'})

        # 更新成功构造响应数据
        address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        return JsonResponse({'code': RETCODE.OK, 'errmsg': '更新地址成功', 'address': address_dict})

    def delete(self, request, address_id):
        """
        删除收货地址
        :param request:
        :param address_id: 要删除的地址ID（路径参数）
        :return: json
        """
        try:
            address = Address.objects.get(id=address_id)

            # 逻辑删除
            address.is_deleted = True
            address.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除收货地址失败'})

        return JsonResponse({'code': RETCODE.OK, 'errmsg': '删除收货地址成功'})


class UpdateDefaultAddressView(mixins.LoginRequiredMixin, View):
    """设置默认地址"""

    def put(self, request, address_id):
        try:
            address = Address.objects.get(id=address_id)
            request.user.default_address = address
            request.user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置默认地址失败'})
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '设置默认地址成功'})


class UpdateAddressTitleView(mixins.LoginRequiredMixin, View):
    """修改地址标题"""

    def put(self, request, address_id):

        title = json.loads(request.body.decode()).get('title')
        try:
            address = Address.objects.get(id=address_id)
            address.title = title
            address.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置地址标题失败'})
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '设置地址标题成功'})


class ChangePasswordView(mixins.LoginRequiredMixin, View):
    """修改密码"""

    def get(self, request):
        return render(request, 'user_center_pass.html')

    def post(self, request):

        old_password = request.POST.get('old_pwd')
        new_password = request.POST.get('new_pwd')
        affirm_new_password = request.POST.get('new_cpwd')

        if not all([old_password, new_password, affirm_new_password]):
            return HttpResponseForbidden('缺少必传参数')
        if not request.user.check_password(old_password):
            return render(request, 'user_center_pass.html', {'origin_pwd_errmsg': '原始密码错误'})
        if not re.match(r'^[0-9a-zA-Z]{8,20}$', new_password):
            return HttpResponseForbidden('请输入8-20位的密码')
        if affirm_new_password != new_password:
            return HttpResponseForbidden('两次输入的密码不一致')

        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception as e:
            logger.error(e)
            return render(request, 'user_center_pass.html', {'change_pwd_errmsg': '修改密码失败'})

        # 修改密码成功后需要重新登录
        logout(request)
        response = redirect(reverse('users:login'))
        response.delete_cookie('username')

        return response
