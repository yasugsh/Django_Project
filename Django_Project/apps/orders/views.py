from django.shortcuts import render
from django_redis import get_redis_connection
from decimal import Decimal
import json
from django import http
from django.utils import timezone
from django.db import transaction
import logging

from Django_Project.utils.views import LoginPassMixin
from users.models import Address
from goods.models import SKU
from .models import OrderInfo, OrderGoods
from Django_Project.utils.response_code import RETCODE


logger = logging.getLogger('django')


# /orders/settlement/
class OrdersSettlementView(LoginPassMixin):
    """订单结算"""

    def get(self, request):
        """生成订单结算页面
        订单结算的数据是从Redis购物车中的已勾选的商品信息"""

        # 查询地址信息
        addresses = Address.objects.filter(user=request.user, is_deleted=False)
        # 如果地址为空，渲染模板时会判断，并跳转到地址编辑页面
        # if addresses.exists() is None:
        if not addresses:
            addresses = None

        redis_conn = get_redis_connection('carts')
        sku_and_count = redis_conn.hgetall('carts_%s' % request.user.id)
        selected = redis_conn.smembers('selected_%s' % request.user.id)
        cart = {}
        for sku_id in selected:
            # 将已勾选的商品对应数量
            cart[int(sku_id)] = int(sku_and_count[sku_id])

        # 所有商品总件数
        total_count = 0
        # 所有商品总金额,Decimal(0.00)写法运算易产生垃圾值
        total_amount = Decimal('0.00')
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            # 给sku属性赋值
            sku.count = cart[sku.id]
            sku.amount = sku.price * sku.count  # 当前sku金额总计
            total_count += sku.count
            total_amount += sku.amount
        # 补充运费
        freight = Decimal('10.00')

        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight  # 实付款
        }

        return render(request, 'place_order.html', context)


# POST /orders/commit/
class OrdersCommit(LoginPassMixin):
    """提交订单(下单)"""

    def post(self, request):
        """保存订单信息和订单商品信息：
        保存到订单的数据是从Redis购物车中的已勾选的商品信息"""

        body_dict = json.loads(request.body.decode())
        address_id = body_dict.get('address_id')
        pay_method = body_dict.get('pay_method')
        user = request.user

        if not all([address_id, pay_method]):
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            return http.HttpResponseForbidden('参数address_id错误')
        if pay_method not in OrderInfo.PAY_METHODS_ENUM.values():
            return http.HttpResponseForbidden('参数pay_method错误')

        # 生成订单编号
        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
        # 订单状态
        status = OrderInfo.ORDER_STATUS_ENUM['UNPAID'] \
            if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY'] \
            else OrderInfo.ORDER_STATUS_ENUM['UNSEND']

        # (手动)显式的开启一个事务
        with transaction.atomic():
            # 创建事务保存点
            save_id = transaction.savepoint()
            try:
                # 保存订单信息
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,  # 订单中所有sku个数
                    total_amount=Decimal('0'),  # 所有sku总价及运费
                    freight=Decimal('10.00'),
                    pay_method=pay_method,
                    status=status
                )

                redis_conn = get_redis_connection('carts')
                redis_carts = redis_conn.hgetall('carts_%s' % user.id)
                selected = redis_conn.smembers('selected_%s' % user.id)
                sku_and_count = {}
                for sku_id in selected:
                    sku_and_count[int(sku_id)] = int(redis_carts[sku_id])

                for sku_id in sku_and_count.keys():
                    # 下单失败可以继续尝试下单
                    while True:
                        sku = SKU.objects.get(id=sku_id)
                        buy_count = sku_and_count[sku_id]
                        # 定义两个变量用来记录当前sku的原本库存和销量
                        origin_stock = sku.stock
                        origin_sales = sku.sales

                        # # 产生脏读、脏写
                        # import time
                        # time.sleep(5)

                        # 如果库存不足就回滚并提前响应
                        if buy_count > origin_stock:
                            # transaction.rollback()
                            transaction.savepoint_rollback(save_id)
                            return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})

                        # 如果能购买，刷新库存和销量
                        new_stock = origin_stock - buy_count
                        new_sales = origin_sales + buy_count

                        # 使用乐观锁(更新数据库前查询当前sku库存)修改数据
                        # 此时会加写入锁，当前事务提交后才解锁，返回修改的记录数量
                        result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock, sales=new_sales)
                        if result == 0:
                            # 下单失败重新下单
                            continue
                        sku.spu.sales += buy_count
                        sku.spu.save()

                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=buy_count,
                            price=sku.price
                        )
                        # 保存商品订单中总数量和总价
                        order.total_count += buy_count
                        order.total_amount += (sku.price * buy_count)

                        # 下单成功就跳出循环
                        break

                # 更改订单中总支付金额
                order.total_amount += order.freight
                order.save()
            except Exception as e:
                logger.error(e)
                # 无论任何类型的错误，暴力回滚到保存点
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '下单失败'})

            # 提交订单成功，(手动)显示的提交此次事务
            # transaction.commit()
            transaction.savepoint_commit(save_id)

        # 生成订单后清除购物车中已结算的商品
        pl = redis_conn.pipeline()
        pl.hdel('carts_%s' % user.id, *selected)
        # pl.srem('selected_%s' % user.id, *selected)
        pl.delete('selected_%s' % user.id)
        pl.execute()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '下单成功', 'order_id': order.order_id})


# GET /orders/success/
class OrderSuccessView(LoginPassMixin):
    """提交订单成功"""

    def get(self, request):
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')

        try:
            OrderInfo.objects.get(order_id=order_id, pay_method=pay_method, total_amount=payment_amount, user=request.user)
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单有误')

        context = {
            'order_id': order_id,
            'payment_amount': payment_amount,
            'pay_method': pay_method
        }

        return render(request, 'order_success.html', context)


# GET /orders/comment/?order_id=xxx
class OrderCommentView(LoginPassMixin):
    """订单评论"""

    def get(self, request):
        """未评价商品进行评价"""

        order_id = request.GET.get('order_id')
        uncomment_goods = OrderGoods.objects.filter(order_id=order_id, is_commented=False)

        uncomment_goods_list = []
        for uncomment_good in uncomment_goods:
            uncomment_goods_list.append({
                'order_id': order_id,
                'sku_id': uncomment_good.sku.id,
                'default_image_url': uncomment_good.sku.default_image.url,
                'name': uncomment_good.sku.name,
                'price': str(uncomment_good.price),
                'display_score': uncomment_good.score
            })

        context = {
            'uncomment_goods_list': uncomment_goods_list
        }
        return render(request, 'goods_judge.html', context)

    def post(self, request):
        """保存评价信息"""

        json_dict = json.loads(request.body.decode())
        order_id = json_dict.get('order_id')
        sku_id = json_dict.get('sku_id')
        comment = json_dict.get('comment')
        score = json_dict.get('score')
        is_anonymous = json_dict.get('is_anonymous')

        if not all([order_id, sku_id, comment, score]):
            return http.JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': "请填写您的评价"})
        if score not in [choices[0] for choices in OrderGoods.SCORE_CHOICES]:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数错误'})

        user = request.user
        try:
            order = OrderInfo.objects.get(order_id=order_id, user_id=user.id)
        except OrderInfo.DoesNotExist:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数order_id错误'})
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数sku_id错误'})

        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                OrderGoods.objects.filter(sku_id=sku.id, order_id=order.order_id, is_commented=False).update(
                    comment=comment, score=score, is_anonymous=is_anonymous, is_commented = True)
                # sku.ordergoods_set.comment = comment
                # sku.ordergoods_set.score = score
                # sku.ordergoods_set.is_anonymous = is_anonymous
                # sku.ordergoods_set.is_commented = True
                # sku.ordergoods_set[0].save()
                sku.comments += 1
                sku.save()
                sku.spu.comments += 1
                sku.spu.save()
            except Exception as e:
                logger.error(e)
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '发表评价失败'})
            transaction.savepoint_commit(save_id)

        uncomment_goods = OrderGoods.objects.filter(order_id=order_id, is_commented=False)
        if not uncomment_goods:
            OrderInfo.objects.filter(order_id=order_id, user_id=user.id).update(
                status=OrderInfo.ORDER_STATUS_ENUM['UNRECEIVED'])

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '发表评价成功'})
