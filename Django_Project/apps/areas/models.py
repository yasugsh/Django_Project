from django.db import models


class Areas(models.Model):
    """省市区"""

    name = models.CharField(max_length=20, verbose_name="名称")
    """
    自关联,related_name指明父级查询子级数据的语法:
    默认'Area模型类对象.area_set'改为'Area模型类对象.subs'
    """
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True, verbose_name="上级行政区")

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '省市区'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
