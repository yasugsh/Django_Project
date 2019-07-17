from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.generics import UpdateAPIView
from rest_framework.decorators import action
from rest_framework.response import Response

from project_admin.utils import PageNum
from project_admin.serializers.orders_manage import OrderInfoSerializer
from orders.models import OrderInfo


# GET /meiduo_admin/orders/?page=1&pagesize=10&keyword=
# GET /meiduo_admin/orders/(?P<order_id>\d+)/
class OrderInfoViewSet(ReadOnlyModelViewSet):
    """订单管理"""

    pagination_class = PageNum
    serializer_class = OrderInfoSerializer
    # 默认是'pk'
    lookup_field = 'order_id'
    # lookup_url_kwarg = 'order_id'

    def get_queryset(self):
        # 当前视图对象中包含当前请求对象
        keyword = self.request.query_params.get('keyword')
        if not keyword or keyword is None:
            return OrderInfo.objects.all().order_by('create_time')
        else:
            return OrderInfo.objects.filter(order_id__contains=keyword).order_by('create_time')

    # PATCH /meiduo_admin/orders/(?P<order_id>\d+)/status/
    @action(methods=['patch'], detail=True)
    def status(self, request, order_id):
        """修改订单状态"""

        order = self.get_object()
        status = request.data.get('status')

        order.status = status
        order.save()

        return Response({
            'order_id': order.order_id,
            'status': order.status
        })
