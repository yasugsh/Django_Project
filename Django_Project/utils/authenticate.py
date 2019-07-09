from django.contrib.auth.backends import ModelBackend
import re
from users.models import User


class UserAuthenticateBackend(ModelBackend):
    """自定义用户认证后端类，增加支持管理员用户登录账号"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        # 判断是否通过vue组件发送请求
        if request is None:
            try:
                user = User.objects.get(username=username, is_staff=True)
            except:
                return None
            # 判断密码
            if user.check_password(password):
                return user
        else:
            try:
                if re.match(r'^1[3-9]\d{9}$', username):
                    user = User.objects.get(mobile=username)
                else:
                    user = User.objects.get(username=username)
            except:
                return None
            if user.check_password(password):
                return user
