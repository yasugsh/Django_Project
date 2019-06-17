from django.contrib.auth import mixins
from django.views.generic.base import View


class LoginPassMixin(mixins.LoginRequiredMixin, View):
    # 用户登录后才能执行的操作(基类)
    pass
