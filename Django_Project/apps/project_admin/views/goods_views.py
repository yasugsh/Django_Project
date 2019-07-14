from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from project_admin.serializers.goods_manage import SKUSerializer, GoodsCategorySerializer, \
    SPUSimpleSerializer, SPUSpecificationSerializer, BrandSerializer, SPUSerializer, SPUOptionSerializer
from project_admin.utils import PageNum
from goods.models import SKU, GoodsCategory, SPU, SPUSpecification, Brand, SpecificationOption


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
                # icontains忽略大小写
                return SKU.objects.filter(name__icontains=keyword).order_by('id')

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
        """获取三级分类数据"""

        categories = self.get_queryset()
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)

    # GET /meiduo_admin/goods/simple/
    def simple(self, request):
        """获取SPU分类数据"""

        spu_set = self.get_queryset()
        serializer = self.get_serializer(spu_set, many=True)
        return Response(serializer.data)

    # GET /meiduo_admin/goods/(?P<pk>\d+)/specs/
    def specs(self, request, pk):
        """获取SPU规格数据"""

        specification_set = self.get_queryset()
        serializer = self.get_serializer(specification_set, many=True)
        return Response(serializer.data)


# /meiduo_admin/goods/?page=<页码>&page_size=<页容量>
class SPUViewSet(ModelViewSet):
    """SPU表管理"""
    pagination_class = PageNum

    def get_queryset(self):
        if self.action == 'brands':
            return Brand.objects.all()
        elif self.action == 'categories':
            pk = self.kwargs.get("pk")
            if pk:
                return GoodsCategory.objects.filter(parent_id=pk)
            return GoodsCategory.objects.filter(parent=None)
        else:
            return SPU.objects.all().order_by('id')

    def get_serializer_class(self):
        if self.action == 'brands':
            return BrandSerializer
        elif self.action == 'categories':
            return GoodsCategorySerializer
        else:
            return SPUSerializer

    # GET /meiduo_admin/goods/brands/simple/
    def brands(self, request):
        """获取品牌信息"""

        brands = self.get_queryset()
        serializer = self.get_serializer(brands, many=True)
        return Response(serializer.data)

    # GET /meiduo_admin/goods/channel/categories/
    # GET /meiduo_admin/goods/channel/categories/(?P<pk>\d+)/
    def categories(self, request, pk=None):
        """获取商品一、二、三级分类信息"""

        categories = self.get_queryset()
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)


# GET /meiduo_admin/goods/specs/?page=1&pagesize=10
# GET /meiduo_admin/goods/simple/
class SpecsViewSet(ModelViewSet):
    """规格表SPUSpecification管理"""

    pagination_class = PageNum
    queryset = SPUSpecification.objects.all().order_by('spu_id')
    serializer_class = SPUSpecificationSerializer


# GET /meiduo_admin/specs/options/?page=1&pagesize=10
class SpecsOptionsViewSet(ModelViewSet):
    """规格选项表SpecificationOption管理"""

    pagination_class = PageNum

    def get_queryset(self):
        if self.action == 'specs':
            return SPUSpecification.objects.all()
        else:
            return SpecificationOption.objects.all().order_by('spec_id')

    def get_serializer_class(self):
        if self.action == 'specs':
            return SPUSpecificationSerializer
        else:
            return SPUOptionSerializer

    # GET /meiduo_admin/goods/specs/simple/
    def specs(self, request):
        """获取SPU所有规格"""

        specification_set = self.get_queryset()
        serializer = self.get_serializer(specification_set, many=True)
        return Response(serializer.data)
