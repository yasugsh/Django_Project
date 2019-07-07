from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView

from .models import SKU
from .serializers import SKUModelSerializer


# GET&POST /goods/
class GoodsListView(GenericAPIView):
    """查询所有对象数据及创建一条新数据"""

    # 构造两个类属性
    queryset = SKU.objects.all()
    serializer_class = SKUModelSerializer

    # lookup_field = 'pk'  # 默认根据pk字段进行过滤
    # lookup_url_kwarg = None  # 根据pk字段在正则分组中提取参数
    # lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

    #     def __init__(self, request, parsers=None, authenticators=None,
    #                  negotiator=None, parser_context=None):
    def get(self, request):
        """
        在进行dispatch()分发前，会对请求进行身份认证、权限检查、流量控制
        :param request: REST framework的Request对象
        :return: REST framework的Response对象
        """

        # get_queryset() 获得数据集 queryset
        goods = self.get_queryset()
        # get_serializer_class() 获得序列化器类 serializer_class
        # get_serializer() 获得序列化器对象
        serializer = self.get_serializer(goods, many=True)

        #     def __init__(self, data=None, status=None,
        #                  template_name=None, headers=None,
        #                  exception=False, content_type=None)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        good_info = request.data
        serializer = self.get_serializer(data=good_info)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# GET&PUT&PATCH&DELETE /goods/(?P<pk>\d+)/
class GoodsDetailView(GenericAPIView):
    """查询、修改、删除单个对象数据"""

    queryset = SKU.objects.all()
    serializer_class = SKUModelSerializer

    def get(self, request, pk):
        # get_object() 根据pk获得单一的数据对象
        good = self.get_object()
        serializer = self.get_serializer(good)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """PUT请求默认为全更新，必传字段都要传"""
        update_data = request.data
        good = self.get_object()
        serializer = self.get_serializer(instance=good, data=update_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, pk):
        """PATCH请求实现部分字段更新"""
        update_data = request.data
        good = self.get_object()

        # partial=True 表示只校验update_data中所传入的字段
        serializer = self.get_serializer(instance=good, data=update_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        good = self.get_object()
        good.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)
