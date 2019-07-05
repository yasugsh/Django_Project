from django.contrib import admin

from goods import models


class GoodsCategoryAdmin(admin.ModelAdmin):
    """运营人员站点中修改数据即触发异步任务"""

    def save_model(self, request, obj, form, change):
        obj.save()
        from celery_tasks.html.tasks import generate_static_list_html
        generate_static_list_html.delay()

    def delete_model(self, request, obj):
        obj.delete()
        from celery_tasks.html.tasks import generate_static_list_html
        generate_static_list_html.delay()


admin.site.register(models.GoodsCategory, GoodsCategoryAdmin)
admin.site.register(models.GoodsChannelGroup)
admin.site.register(models.GoodsChannel)
admin.site.register(models.Brand)
admin.site.register(models.SPU)
admin.site.register(models.SKU)
admin.site.register(models.SKUImage)
admin.site.register(models.SPUSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKUSpecification)
admin.site.register(models.GoodsVisitCount)
