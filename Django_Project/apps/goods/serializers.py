from rest_framework import serializers

from .models import SKU


class SKUModelSerializer(serializers.ModelSerializer):
    """SKU模型类序列化器"""

    class Meta:
        model = SKU
        fields = '__all__'
