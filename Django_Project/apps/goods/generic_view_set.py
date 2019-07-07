from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination

from .models import SKU
from .serializers import SKUModelSerializer


class GoodsSetPagePagination(PageNumberPagination):
    """自定义PageNumberPagination分页类"""

    # 每页数目
    page_size = 5
    # 前端发送的所要查找的页数关键字名，默认为"page"
    page_query_param = 'page'
    # 前端发送的设置每页数目关键字名，默认为None
    page_size_query_param = 'page_size'
    # 前端最多能设置的每页数量
    max_page_size = 10


class GoodsSetOffsetPagination(LimitOffsetPagination):
    """自定义LimitOffsetPagination分页类"""

    # 默认限制每页数目
    default_limit = 5
    # 前端发送的所要查找多少条数据关键字名，默认为'limit'
    limit_query_param = 'limit'
    # 前端发送的所要偏移条数的关键字名，默认为'offset'
    offset_query_param = 'offset'
    # 最大limit限制，默认None
    max_limit = 10


# GET /goods_set/
class GoodsViewSet(ListModelMixin, GenericViewSet):
    queryset = SKU.objects.all().order_by('-sales')
    serializer_class = SKUModelSerializer
    # pagination_class = GoodsSetPagePagination
    pagination_class = GoodsSetOffsetPagination
