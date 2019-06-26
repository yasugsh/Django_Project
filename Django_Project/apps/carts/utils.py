import pickle, base64
from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, response):
    """
    登录时合并购物车
    :param request: 登录的请求对象
    :param response: 删除cookie的响应对象
    :return:.

    """

    cart_str = request.COOKIES.get('carts')
    if cart_str:
        cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
    else:
        return

    redis_conn = get_redis_connection('carts')
    pl = redis_conn.pipeline()

    for sku_id, count_selected in cart_dict.items():
        # 如果hash中sku_id已存在,就直接覆盖,不存在就新增
        pl.hset('carts_%s' % request.user.id, sku_id, count_selected['count'])
        # 如果当前sku_id在cookie购物车中为勾选,就将sku_id存储到set集合
        if count_selected['selected']:
            pl.sadd('selected_%s' % request.user.id, sku_id)
        else:
            pl.srem('selected_%s' % request.user.id, sku_id)
    pl.execute()

    # 合并后删除cookie购物车数据
    response.delete_cookie('carts')
