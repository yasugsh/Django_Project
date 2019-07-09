from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler


class LoginSerializer(serializers.Serializer):
    """自定义登录签发JWT的视图"""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    token = serializers.CharField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)

    def validate(self, attrs):
        """验证用户名和密码"""

        user = authenticate(**attrs)

        if not user:
            raise serializers.ValidationError("用户名或密码错误")

        user_payload = jwt_payload_handler(user)
        jwt_token = jwt_encode_handler(user_payload)

        # 返回有效数据
        return {
            'username': user.username,
            'user_id': user.id,
            'token': jwt_token
        }
