from django.shortcuts import render
from django import http
from alipay import AliPay
from django.conf import settings
import os
from django.views.generic.base import View

from Django_Project.utils.views import LoginPassMixin
from orders.models import OrderInfo
from Django_Project.utils.response_code import RETCODE
from .models import Payment


# GET /payment/(?P<order_id>\d+)/
class PaymentView(LoginPassMixin):
    """订单支付功能(去支付)"""

    def get(self, request, order_id):
        """查询要支付的订单,生成支付宝登录的链接"""
        user = request.user
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单信息错误')

        # 创建支付宝支付对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/alipay_public_key.pem"),
            sign_type="RSA2",  # 必须与支付宝上加密方式一致
            debug=settings.ALIPAY_DEBUG  # True表示沙箱环境
        )

        # 生成支付宝登录网页链接
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject="Project_%s" % order_id,
            return_url=settings.ALIPAY_RETURN_URL,  # 默认回调url
            app_notify_url=None,  # 默认为None,必须是公网上线的域名
        )

        # 响应登录支付链接
        # 真实环境电脑网站支付网关：https://openapi.alipay.com/gateway.do? + order_string
        # 沙箱环境电脑网站支付网关：https://openapi.alipaydev.com/gateway.do? + order_string
        alipay_url = settings.ALIPAY_URL + "?" + order_string
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'alipay_url': alipay_url})


# GET /payment/status/
class PaymentStatusView(View):
    """保存订单支付结果，继承View，
    支付宝可以在用户退出登录的状态下回调app_notify_url地址发送post请求回传订单支付结果"""

    def get(self, request):
        # 获取前端传入的请求参数
        data = request.GET.dict()
        # 从请求参数中删除signature
        signature = data.pop('sign')

        # 创建支付宝支付对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/alipay_public_key.pem"),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )

        # 校验此回调url是否是从alipay重定向过来的：True or False
        success = alipay.verify(data, signature)
        if success:
            # 读取订单号
            order_id = data.get('out_trade_no')
            # 读取支付宝流水号
            trade_id = data.get('trade_no')

            try:
                Payment.objects.get(trade_id=trade_id, order_id=order_id)
            except Payment.DoesNotExist:
                # 保存Payment模型类数据
                Payment.objects.create(
                    trade_id=trade_id,
                    order_id=order_id
                )
            # 修改订单状态为待评价
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(
                status=OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT'])

            # 响应流水号
            context = {
                'trade_id': trade_id
            }
            return render(request, 'pay_success.html', context)
        else:
            # 订单支付失败，重定向到我的订单
            return http.HttpResponseForbidden('非法请求')
