from django.db import models

from Django_Project.utils.models import BaseModel


class OAuthSinaUser(BaseModel):
    """微博用户登录模型类"""

    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name="用户名")
    uid = models.CharField(max_length=64, verbose_name="uid", db_index=True)

    class Meta:
        db_table = "tb_oauth_sina"
        verbose_name = "微博登录用户数据"
        verbose_name_plural = verbose_name
