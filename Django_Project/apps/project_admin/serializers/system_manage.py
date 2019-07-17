from rest_framework import serializers
from django.contrib.auth.models import Permission, ContentType, Group
from django.contrib.auth.hashers import make_password

from users.models import User


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


class OperateUserSerializer(serializers.ModelSerializer):
    """运营用户数据序列化器"""

    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email', 'password', 'groups', 'user_permissions']

        # username字段增加长度限制，password字段只参与保存
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20
            },
            'password': {
                'min_length': 8,
                'max_length': 20,
                'write_only': True
            },
        }

    # 重写create方法创建运营用户，并创建中间表数据
    def create(self, validated_data):
        # groups = validated_data.pop('groups')
        # user_permissions = validated_data.pop('user_permissions')
        # instance = User.objects.create_user(**validated_data)
        #
        # # 设置is_staff为True
        # instance.is_staff = True
        # # 创建用户与组以及用户与权限的两个中间表数据
        # instance.groups.set(groups)
        # instance.user_permissions.set(user_permissions)
        # instance.save()
        #
        # return instance

        # validated_data['is_staff'] = True
        # # 调用父类create方法，会自动创建用户与组以及用户与权限的两个中间表数据
        # instance = super().create(validated_data)
        #
        # # 将用户密码加密后再保存
        # instance.set_password(instance.password)
        # instance.save()
        #
        # return instance

        validated_data['is_staff'] = True
        validated_data['password'] = make_password(validated_data['password'])
        # 调用父类create方法，会自动创建用户与组以及用户与权限的两个中间表数据
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        # 调用父类update方法，会自动更新两个中间表数据
        return super().update(instance, validated_data)
