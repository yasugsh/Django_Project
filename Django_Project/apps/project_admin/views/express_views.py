from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import User
from project_admin.serializers.express_manage import PlaceOrderSerializer
from project_admin.tasks import celery_place_order
from project_admin.models import ExpressInfo
from project_admin.project_express.project_express import ProjectExpress


class ExpressViewSet(ViewSet):
    """订单物流管理"""

    def get_permissions(self):
        """
        重写该函数实现:
        1、下单接口必须是超级管理员调用
        2、查询接口只需经过身份认证即可
        """
        if self.action in ['place_order', 'userinfo']:
            return [IsAdminUser()]
        elif self.action == "prompt_check":
            return [IsAuthenticated()]

    # GET meiduo_admin/express/(?P<pk>\d+)/userinfo/
    @action(methods=['get'], detail=True)
    def userinfo(self, request, pk):
        """根据订单号获取寄件及收件人信息"""

        Sender = request.user
        Receiver = User.objects.get(orderinfo__order_id=pk)

        return Response({
            "Sender": {
                "Name": Sender.username,
                "Mobile": Sender.mobile,
                "ProvinceName": Sender.default_address.province.name,
                "CityName": Sender.default_address.city.name,
                "ExpAreaName": Sender.default_address.district.name,
                "Address": Sender.default_address.place
            },
            "Receiver": {
                "Name": Receiver.username,
                "Mobile": Receiver.mobile,
                "ProvinceName": Receiver.default_address.province.name,
                "CityName": Receiver.default_address.city.name,
                "ExpAreaName": Receiver.default_address.district.name,
                "Address": Receiver.default_address.place
            },
        })

    # POST meiduo_admin/express/place_order/
    @action(methods=['post'], detail=False)
    def place_order(self, request):
        """快递下单"""

        serializer = PlaceOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 创建快递操作对象
        express = ProjectExpress()
        result = express.place_order(request_data=serializer.validated_data)

        if result.get('Success'):
            ExpressInfo.objects.create(
                order_id=result['Order']['OrderCode'],
                staff_id=request.user.id,
                logistic_code=result['Order']['LogisticCode'],  # 快递单号
                shipper_code=result['Order']['ShipperCode']  # 快递公司编码
            )
            return Response({"result": True})
        return Response({"result": False})

    # GET meiduo_admin/express/(?P<pk>\d+)/prompt_check/
    @action(methods=['get'], detail=True)
    def prompt_check(self, request, pk):
        """快递物流查询"""

        express_info = ExpressInfo.objects.get(order_id=pk)

        # 创建快递操作对象
        express = ProjectExpress()

        result = express.prompt_check(request_data={
            "OrderCode": express_info.order_id,
            "ShipperCode": express_info.shipper_code,
            "LogisticCode": express_info.logistic_code
        })
        return Response(result)
