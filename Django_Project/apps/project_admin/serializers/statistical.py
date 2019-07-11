from rest_framework import serializers

from goods.models import GoodsVisitCount


class GoodsSerializer(serializers.ModelSerializer):
    """商品及所在三级分类的序列化器"""

    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = GoodsVisitCount
        fields = ['count', 'category']
