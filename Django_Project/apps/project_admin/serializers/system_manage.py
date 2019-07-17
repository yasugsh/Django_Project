from rest_framework import serializers
from django.contrib.auth.models import Permission, ContentType, Group


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


class GroupSerializer(serializers.ModelSerializer):
    """用户组表Group序列化器"""

    class Meta:
        model = Group
        # permissions = models.ManyToManyField() 多对多关系，
        # permissions字段为一个permission的id组成的列表，
        # 创建Group表数据时，自动添加中间表数据
        fields = ['id', 'name', 'permissions']
