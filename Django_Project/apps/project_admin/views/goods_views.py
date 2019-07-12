from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from project_admin.serializers.goods_manage import SKUSerializer, GoodsCategorySerializer, \
    SPUSimpleSerializer, SPUSpecificationSerializer
from project_admin.utils import PageNum
from goods.models import SKU, GoodsCategory, SPU, SPUSpecification


# /meiduo_admin/skus/?page=<页码>&page_size=<页容量>&keyword=<名称|副标题>
class SKUViewSet(ModelViewSet):
    """SKU的增删改查"""
    pagination_class = PageNum

    # 重写get_queryset方法，根据前端是否传递keyword值返回不同查询集
    def get_queryset(self):
        if self.action == 'categories':
            # parent_id大于37为三级分类信息
            return GoodsCategory.objects.filter(parent_id__gt=37)
        elif self.action == 'simple':
            return SPU.objects.all()
        elif self.action == 'specs':
            # 获取spu_id，路径参数
            pk = self.kwargs['pk']
            return SPUSpecification.objects.filter(spu_id=pk)
        else:
            keyword = self.request.query_params.get('keyword')
            if not keyword or keyword is None:
                return SKU.objects.all().order_by('id')
            else:
                return SKU.objects.filter(name__contains=keyword).order_by('id')

    # 根据请求资源不同返回不同的序列化器
    def get_serializer_class(self):
        if self.action == 'categories':
            return GoodsCategorySerializer
        elif self.action == 'simple':
            return SPUSimpleSerializer
        elif self.action == 'specs':
            return SPUSpecificationSerializer
        else:
            return SKUSerializer

    # GET /meiduo_admin/skus/categories/
    @action(methods=['get'], detail=False)
    def categories(self, request):
        """获取当前SKU的三级分类信息"""

        categories = self.get_queryset()
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)

    # GET /meiduo_admin/goods/simple/
    @action(methods=['get'], detail=False)
    def simple(self, request):
        """获取SKU的SPU表名称数据"""

        spu_set = self.get_queryset()
        serializer = self.get_serializer(spu_set, many=True)
        return Response(serializer.data)

    # GET /meiduo_admin/goods/(?P<pk>\d+)/specs/
    @action(methods=['get'], detail=True)
    def specs(self, request, pk):
        """获取SPU商品规格信息"""

        specification_set = self.get_queryset()
        serializer = self.get_serializer(specification_set, many=True)
        return Response(serializer.data)
