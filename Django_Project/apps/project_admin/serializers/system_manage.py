from rest_framework import serializers
from django.contrib.auth.models import Permission, ContentType


class PermissionSerializer(serializers.ModelSerializer):
    """用户权限控制表Permission序列化器"""

    class Meta:
        model = Permission
        fields = '__all__'


class ContentTypeSerializer(serializers.ModelSerializer):
    """权限类型表ContentType序列化器"""

    class Meta:
        model = ContentType
        fields = ['id', 'name']
