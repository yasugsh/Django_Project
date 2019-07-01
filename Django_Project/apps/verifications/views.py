import random, logging, re, json
from django.views.generic.base import View
from django_redis import get_redis_connection
from django.http import HttpResponse, JsonResponse

from Django_Project.utils.response_code import RETCODE, err_msg
from .libs.captcha.captcha import captcha  # 导入生成验证码的对象
from . import constants  # 导入常量文件
# from verifications.libs.yuntongxun.sms import *  # 导入云通讯中发送短信验证码的辅助类
from celery_tasks.sms.tasks import send_sms_code
from users.models import User
from verifications.utils import generate_user_info_signature, check_user_info_signature


logger = logging.getLogger('django')


# GET image_codes/(?P<uuid>[\w-]+)/
class ImageCodeView(View):
    """图形验证码"""

    def get(self, request, uuid):
        """
        :param request: 请求对象
        :param uuid: 唯一标识图形验证码所属的用户
        :return: image/jpg
        """
        # 通过captcha对象的generate_captcha方法生成图片验证码
        name, text, image_bytes = captcha.generate_captcha()

        # 保存图片验证码到redis数据库(string类型,300s过期)
        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        # 响应图片数据
        return HttpResponse(image_bytes, content_type='image/jpg')


# GET /sms_codes/(?P<mobile>1[3-9]\d{9})/?image_code=&uuid=
class SMSCodeView(View):
    """短信验证码"""

    def get(self, request, mobile):
        """
        :param request: 请求对象
        :param mobile: 手机号
        :return: JSON
        """
        redis_conn = get_redis_connection('verify_code')

        # 发短信之前用当前手机号获取redis中短信已发的标记,如果有则表示60秒内发送过短信
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            data ={
                'code': RETCODE.THROTTLINGERR,
                'errmsg': '发送短信过于频繁'
            }
            return JsonResponse(data)

        # 接收参数
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')

        if not all([image_code_client, uuid]):
            data = {
                'code': RETCODE.NECESSARYPARAMERR,
                'errmsg': err_msg[RETCODE.NECESSARYPARAMERR]
            }
            return JsonResponse(data)

        # 提取图形验证码
        image_code_server = redis_conn.get('img_%s' % uuid)

        # 避免用户使用图形验证码恶意测试，后端提取了redis图形验证码后，立即删除
        redis_conn.delete('img_%s' % uuid)

        if image_code_server is None:  # 图形验证码过期或者不存在
            data = {
                'code': RETCODE.IMAGECODEERR,
                'errmsg': '图形验证码失效'
            }
            return JsonResponse(data)

        # 对比图形验证码(redis中取出来的数据都是bytes类型)
        if image_code_client.lower() != image_code_server.decode().lower():
            data = {
                'code': RETCODE.IMAGECODEERR,
                'errmsg': '输入的图形验证码有误'
            }
            return JsonResponse(data)

        # 随机生成一个6位整数作为短信验证码
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)

        # 创建redis管道对象,再将Redis请求添加到管道(队列)
        pl = redis_conn.pipeline()
        # 将短信验证码保存到redis中(300秒)
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 发送短信之后保存一个已发送的标记到redis中,避免频繁发送短信验证码
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 执行管道
        pl.execute()

        """
        通过CCP类对象发送短信验证码:
        CCP().send_template_sms('18218576911', ['123456', 5], 1)
        """
        # CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], constants.SEND_SMS_TEMPLATE_ID)
        # 添加发送短信的任务到Celery异步任务队列
        send_sms_code.delay(mobile, sms_code)

        data = {
            'code': RETCODE.OK,
            'errmsg': '发送短信验证码成功'
        }
        return JsonResponse(data)


# GET /accounts/(?P<username>[a-zA-Z0-9_-]{5,20})/sms/token/?text=xxx&image_code_id=xxx
class CheckImageCodeView(View):
    """找回密码验证图形验证码"""

    def get(self, request, username):

        image_code_client = request.GET.get('text')
        uuid = request.GET.get('image_code_id')

        redis_conn = get_redis_connection('verify_code')
        image_code_server = redis_conn.get('img_%s' % uuid)

        if image_code_server is None:
            return JsonResponse({"code":RETCODE.IMAGECODEERR, "errmsg": "图形验证码失效"})
        redis_conn.delete("img_%s" % uuid)

        if image_code_client.lower() != image_code_server.decode().lower():
            return JsonResponse({"code": RETCODE.IMAGECODEERR, "errmsg": "图形验证码输入错误"})

        try:
            if re.match(r"^1[3-9]\d{9}", username):
                user = User.objects.get(mobile=username)
            else:
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({"code":RETCODE.DBERR, "errmsg": "用户名或手机号不存在"})

        mobile = str(user.mobile)
        hide_mobile = mobile[0:3] + '****' + mobile[-4:]
        access_token = generate_user_info_signature(mobile)

        data = {
            'mobile': hide_mobile,
            'access_token': access_token
        }

        return JsonResponse(data=data)


# GET /sms_codes/?access_token=xxx
class SendSMSCodeView(View):
    """找回密码发送短信验证码"""

    def get(self, request):

        access_token = request.GET.get('access_token')
        mobile = check_user_info_signature(access_token)

        # 从redis数据库中获取标识
        redis_conn = get_redis_connection("verify_code")
        send_flg = redis_conn.get("send_flg_%s" % mobile)
        # 判斷标识有没有到期
        if send_flg:
            return JsonResponse({"code": RETCODE.THROTTLINGERR, "errmsg": "短信发送过于频繁"})

        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            return JsonResponse({"code": RETCODE.DBERR, "errmsg": "用户名或手机号不存在"})

        sms_code = "%06d" % random.randint(0, 999999)
        print(sms_code)

        pl = redis_conn.pipeline()

        pl.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex("send_flg_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, 1)

        pl.execute()
        # # 手机发短信
        # CCP().send_template_sms(mobile,[sms_code,constants.SMS_CODE_REDIS_EXPIRES // 60],1)

        send_sms_code.delay(mobile,sms_code)

        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})


# GET /accounts/(?P<username>[a-zA-Z0-9_-]{5,20})/password/token/?sms_code=xxx
class CheckSMSCodeView(View):
    """找回密码验证短信验证码"""

    def get(self, request, username):

        sms_code_client = request.GET.get('sms_code')

        try:
            if re.match(r"^1[3-9]\d{9}", username):
                user = User.objects.get(mobile=username)
            else:
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({"code":RETCODE.DBERR, "errmsg": "用户名或手机号不存在"})

        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % user.mobile)
        if sms_code_server is None:
            return JsonResponse({"code":RETCODE.SMSCODERR, "errmsg": "短信验证码失效"})
        redis_conn.delete("img_%s" % user.mobile)

        if sms_code_client != sms_code_server.decode():
            return JsonResponse({"code": RETCODE.SMSCODERR, "errmsg": "短信验证码输入错误"})

        access_token = generate_user_info_signature(user.password)

        data = {
            'user_id': user.id,
            'access_token': access_token
        }

        return JsonResponse(data=data)


# POST /users/(?P<user_id>\d+)/password/
class ResetPasswordView(View):
    """完成密码重置"""

    def post(self, request, user_id):

        json_dict = json.loads(request.body.decode())
        pwd = json_dict.get('password')
        cpwd = json_dict.get('password2')
        access_token = json_dict.get('access_token')

        if all([pwd, cpwd, access_token]) is False:
            return JsonResponse({"code": RETCODE.NECESSARYPARAMERR, "message": "缺少必传参数"})
        if not re.match(r'^[0-9A-Za-z]{8,20}$', pwd):
            return JsonResponse({"code":RETCODE.CPWDERR, "message": "密码格式错误"})
        if cpwd != pwd:
            return JsonResponse({"code":RETCODE.CPWDERR, "message": "两次输入的密码不一致"})

        user_password = check_user_info_signature(access_token)
        try:
            user = User.objects.get(id=user_id, password=user_password)
        except User.DoesNotExist:
            return JsonResponse({"code":RETCODE.DBERR, "message": "用户不存在"})

        try:
            user.set_password(pwd)
            user.save()
        except:
            return JsonResponse({"code":RETCODE.DBERR, "message": "修改密码失败"})

        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
