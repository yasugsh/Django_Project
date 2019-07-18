from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    """快递寄件及收件人信息序列化器"""

    Name = serializers.CharField()
    Tel = serializers.CharField(required=False)
    Mobile = serializers.CharField(required=False)
    ProvinceName = serializers.CharField()
    CityName = serializers.CharField()
    ExpAreaName = serializers.CharField()
    Address = serializers.CharField()

    def validate(self, attrs):
        if not (attrs.get('Mobile') or attrs.get('Tel')):
            raise serializers.ValidationError('手机和电话必须有一个')
        return attrs


class CommoditySerializer(serializers.Serializer):
    """订单商品序列化器"""

    GoodsName = serializers.CharField()


class PlaceOrderSerializer(serializers.Serializer):
    """快递下单序列化器，用来生成快递信息"""

    OrderCode = serializers.CharField()  # 订单编号
    ShipperCode = serializers.CharField()  # 快递公司编码
    PayType = serializers.IntegerField()  # 运费支付方式
    ExpType = serializers.IntegerField()  # 快递类型
    Sender = UserSerializer()  # 寄件人
    Receiver = UserSerializer()  # 收件人
    Commodity = CommoditySerializer(many=True)  # 订单商品名称
    Quantity = serializers.IntegerField()  # 包裹数

    def validate(self, attrs):
        # 如果是中通订单,需要添加客户号
        # 具体哪些物流公司需要客户号请查看《快递鸟电子面单客户号参数对照表.xlsx》
        if attrs.get("ShipperCode") == "ZTO":
            attrs['CustomerName'] = 'testzto'
            attrs['CustomerPwd'] = 'testztopwd'

        return attrs
