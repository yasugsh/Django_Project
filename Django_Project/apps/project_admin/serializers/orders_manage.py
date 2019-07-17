from rest_framework import serializers

from orders.models import OrderInfo, OrderGoods
from project_admin.serializers.goods_manage import SKUSimpleSerializer


class OrderGoodsSerializer(serializers.ModelSerializer):
    """OrderGoods模型类序列化器"""

    sku = SKUSimpleSerializer(read_only=True)

    class Meta:
        model = OrderGoods
        fields = ['id', 'count', 'price', 'sku']


class OrderInfoSerializer(serializers.ModelSerializer):
    """OrderInfo模型类序列化器"""

    user = serializers.StringRelatedField(read_only=True)
    skus = OrderGoodsSerializer(read_only=True, many=True)

    class Meta:
        model = OrderInfo
        fields = '__all__'
