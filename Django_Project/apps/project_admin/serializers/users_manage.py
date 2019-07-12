from rest_framework import serializers
from users.models import User
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    """User模型类序列化器"""

    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email', 'password']

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

    # 1、重写validate方法进行密码加密及is_staff=True
    def validate(self, attrs):
        """
        数据校验或构建，返回的有效数据传递给create方法用来构建新的模型类对象
        :param attrs: 前端传入的数据
        :return: 校验成功的有效数据
        """
        # 将密码加密处理
        attrs['password'] = make_password(attrs['password'])
        attrs['is_staff'] = True
        return attrs

    # 2、重写create方法进行密码加密及is_staff=True
    # def create(self, validated_data):
    #     return User.objects.create_superuser(**validated_data)
