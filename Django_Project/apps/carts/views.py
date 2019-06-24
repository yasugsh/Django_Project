from django.shortcuts import render
from django.views.generic.base import View
import json, pickle, base64
from django import http
from django_redis import get_redis_connection

from goods.models import SKU
from Django_Project.utils.response_code import RETCODE
from . import constants


# GET&POST&PUT&DELETE /carts/
class CartsView(View):
    """购物车管理"""

    def post(self, request):
        """添加购物车数据"""
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        # 前端未传勾选状态，默认已勾选
        selected = json_dict.get('selected', True)

        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断sku_id是否存在
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('商品不存在')

        try:
            # 类型转换成功说明count参数为类整型数据
            count = int(count)
        except Exception:
            return http.HttpResponseForbidden('参数count有误')

        if selected:
            # 判断selected是否为bool类型实例对象
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected有误')

        user = request.user
        response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})

        if user.is_authenticated:
            # 用户已登录，操作redis
            """
            carts_1: {sku_1: count, sku_3: count, sku_5: count, ...}
            selected_1: {sku_1, sku_3, ...}
            """
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # hincrby(key, field, amount)
            # 如果key不存在则添加一条hash数据
            # 如果key存在则将key映射的value中amount叠加
            pl.hincrby('carts_%s' % user.id, sku_id, count)
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            pl.execute()
        else:
            # 用户未登录，操作cookie
            """
            {
                "sku_1": {"count": "1", "selected": "True"},
                "sku_3": {"count": "3", "selected": "True"},
                "sku_5": {"count": "2", "selected": "False"}
            }
            """
            cart_str = request.COOKIES.get('carts')
            if cart_str:  # 如果用户已经添加过cookie购物车数据
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
                # 如果sku_id已经在字典中,直接将count与之前的sku数量相加
                if sku_id in cart_dict:
                    origin_count = cart_dict[sku_id]['count']
                    count += origin_count
            else:
                cart_dict = {}

            # 如果sku_id已在字典中,进行修改,未在字典中则添加新键值对
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 将字典转成bytes,再将bytes转成base64的bytes,最后将base64的bytes转字符串
            cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            response.set_cookie('carts', cookie_cart_str, max_age=constants.CARTS_COOKIE_EXPIRES)

        return response

    def get(self, request):
        """展示购物车"""
        user = request.user
        if user.is_authenticated:
            # 登录用户，查询redis购物车
            redis_conn = get_redis_connection('carts')
            redis_cart = redis_conn.hgetall('carts_%s' % user.id)
            cart_selected = redis_conn.smembers('selected_%s' % user.id)

            # 将redis中的数据构造成跟cookie中的格式一致，方便统一操作
            cart_dict = {}
            for sku_id, count in redis_cart.items():
                # sku_id与count取出来都是bytes类型
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in cart_selected  # bool值
                }
        else:
            # 未登录用户，查询cookie购物车
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

        skus = SKU.objects.filter(id__in=cart_dict.keys())
        cart_skus = []
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                # 将True或False转为字符串格式,方便json解析
                'selected': str(cart_dict.get(sku.id).get('selected')),
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                # 从Decimal('10.2')中取出'10.2'，方便json解析
                'price': str(sku.price),
                'count': cart_dict.get(sku.id).get('count'),
                'amount': str(sku.price * cart_dict.get(sku.id).get('count'))
            })
        context = {
            'cart_skus': cart_skus
        }

        return render(request, 'cart.html', context)

    def put(self, request):
        """修改购物车"""
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断sku_id是否存在
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('商品不存在')

        try:
            # 类型转换成功说明count参数为类整型数据
            count = int(count)
        except Exception:
            return http.HttpResponseForbidden('参数类型错误')

        # 判断selected是否为bool类型实例对象
        if not isinstance(selected, bool) or count < 0:
            return http.HttpResponseForbidden('参数类型错误')

        user = request.user
        cart_sku = {
            'id': sku.id,
            'selected': selected,
            'default_image_url': sku.default_image.url,
            'name': sku.name,
            # 从Decimal('10.2')中取出'10.2'，方便json解析
            'price': str(sku.price),
            'count': count,
            'amount': str(sku.price * count)
        }
        response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})

        if user.is_authenticated:
            # 登录用户，修改redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # 因为接口设计为幂等的，key存在就直接覆盖
            pl.hset('carts_%s' % user.id, sku_id, count)
            if selected:
                # 自动去重
                pl.sadd('selected_%s' % user.id, sku_id)
            else:
                # 数据不存在自动忽略
                pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()
        else:
            # 未登录用户，修改cookie购物车
            cart_str = request.COOKIES.get('carts')
            # 判断是否有cookie购物车数据
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '未获取到cookie数据'})
            # 因为接口设计为幂等的，key存在就直接覆盖
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            response.set_cookie('carts', cookie_cart_str, max_age=constants.CARTS_COOKIE_EXPIRES)

        return response

    def delete(self, request):
        """删除购物车"""
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        # 判断sku_id是否存在
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('商品不存在')

        user = request.user
        response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除购物车成功'})

        if user.is_authenticated:
            # 登录用户，删除redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # 删除键，就等价于删除了整条记录，数据不存在自动忽略
            pl.hdel('carts_%s' % user.id, sku_id)
            pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()
        else:
            # 未登录用户，删除cookie购物车
            cart_str = request.COOKIES.get('carts')

            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '未获取到cookie数据'})
            if sku_id in cart_dict:
                del cart_dict[sku_id]

            # 如果购物车字典中的数据都已删完,就删除当前cookie
            if not cart_dict:  # '' () {} []
                # 删除cookie的原理就是在设置cookie把它的过期时间设置为0
                response.delete_cookie('carts')
                return response

            cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            response.set_cookie('carts', cookie_cart_str, max_age=constants.CARTS_COOKIE_EXPIRES)

        return response


# PUT /carts/selection/
class CartsSelectAllView(View):
    """购物车全选"""

    def put(self, request):
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get('selected')

        if not isinstance(selected, bool):
            return http.HttpResponseForbidden('参数类型错误')

        user = request.user
        response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

        if user.is_authenticated:
            # 登录用户，操作redis购物车
            redis_conn = get_redis_connection('carts')
            sku_and_count = redis_conn.hgetall('carts_%s' % user.id)
            if selected:
                # 全选,将所有的sku_id添加到set集合
                redis_conn.sadd('selected_%s' % user.id, *sku_and_count.keys())
            else:
                # 取消全选,删除set集合中所有的sku_id或直接将set集合删除
                # redis_conn.srem('selected_%s' % user.id, *sku_and_count.keys())
                redis_conn.delete('selected_%s' % user.id)
        else:
            # 未登录用户，操作cookie购物车
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '无购物车'})

            for sku_id in cart_dict:
                # 修改cookie字典中所有sku_id的勾选状态
                cart_dict[sku_id]['selected'] = selected
            cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            response.set_cookie('carts', cart_str, constants.CARTS_COOKIE_EXPIRES)

        return response
