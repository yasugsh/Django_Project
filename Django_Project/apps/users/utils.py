from django.contrib.auth.backends import ModelBackend
import re
from .models import User


def get_user_by_account(account):
    """
    根据account查询用户
    :param account: 前端表单框输入的用户名或手机号
    :return: user对象(未认证密码)
    """
    try:
        if re.match(r'^1[3-9]\d{9}$', account):
            # 匹配成功表示为手机号登录
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    return user


class UsernameMobileAuthBackend(ModelBackend):
    """自定义用户认证后端类"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        重写认证方法，实现多账号登录
        :param request: 请求对象
        :param username: 用户名或者手机号
        :param password: 密码
        :param kwargs: 其他参数
        :return: 密码认证通过的user对象
        """

        # 根据传入的username获取user对象,username可以是用户名或手机号
        user = get_user_by_account(username)
        if user and user.check_password(password):
            return user
