from django.shortcuts import render
from django.views.generic.base import View
from django_redis import get_redis_connection
from django.http import HttpResponse

from .libs.captcha.captcha import captcha  # 导入生成验证码的对象
from . import constants  # 导入常量文件


class ImageCodeView(View):
    """图形验证码"""

    def get(self, request, uuid):
        """
        :param request: 请求对象
        :param uuid: 唯一标识图形验证码所属的用户
        :return: image/jpg
        """
        # 通过captcha对象的generate_captcha方法生成图片验证码
        name, text, image = captcha.generate_captcha()

        # 保存图片验证码到redis数据库(string类型,300s过期)
        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        # 响应图片验证码
        return HttpResponse(image, content_type='image/jpg')

