from django.shortcuts import render
from django_redis import get_redis_connection
from decimal import Decimal

from Django_Project.utils.views import LoginPassMixin
from users.models import Address
from goods.models import SKU


# /orders/settlement/
class OrdersSettlementView(LoginPassMixin):
    """订单结算"""

    def get(self, request):
        """生成订单结算页面"""

        # 查询地址信息
        addresses = Address.objects.filter(user=request.user, is_deleted=False)
        # 如果地址为空，渲染模板时会判断，并跳转到地址编辑页面
        if not addresses.exists():
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
