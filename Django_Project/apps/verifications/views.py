import random
import logging
from django.shortcuts import render
from django.views.generic.base import View
from django_redis import get_redis_connection
from django.http import HttpResponse, JsonResponse

from Django_Project.utils.response_code import RETCODE, err_msg
from .libs.captcha.captcha import captcha  # 导入生成验证码的对象
from . import constants  # 导入常量文件
# from verifications.libs.yuntongxun.sms import *  # 导入云通讯中发送短信验证码的辅助类
from celery_tasks.sms.tasks import send_sms_code


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
