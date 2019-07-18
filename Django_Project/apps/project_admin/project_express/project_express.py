from .kdbird_express.request_type import *
from .kdbird_express.kdbird_express import KDBirdExpress
from .kdbird_express.request_urls import *

class ProjectExpress(KDBirdExpress):
    """
    我们需要在这个类中重写虚基类函数实现快递查询下单等接口
    """

    def place_order(self, request_data):
        """
        快递下单
        请求报文中不能出现字符：' " # & + < > % \
        自动订阅
        订单编号 OrderCode 可自定义，不可重复
        :param request_data:
        {
            "ShipperCode": 快递公司编码，
            "OrderCode": 订单编号(自定义，不可重复)
            "PayType": 运费支付方式, 1-现付，2-到付，3-月结，4-第三方付(仅SF支持)
            "ExpType": 快递类型,默认为1-标准快递
            "Receiver": {
                "Name": 收件人姓名,
                "Tel": 收件人手机,
                "Mobile": 收件人电话,
                "ProvinceName": 省,
                "CityName": 市,
                "ExpAreaName": 区/县(具体名称中不要缺少"区"或"县"),
                "Address": 详细地址,
                "PostCode": 收件地邮编(ShipperCode为EMS、YZPY、YZBK 时必填)
            },
            "Sender": {
                "Name": 发件人姓名,
                "Tel": 发件人手机,
                "Mobile": 发件人电话,
                "ProvinceName": 省,
                "CityName": 市,
                "ExpAreaName": 区/县(具体名称中不要缺少"区"或"县"),
                "Address": 详细地址,
                "PostCode": 发件地邮编(ShipperCode为EMS、YZPY、YZBK 时必填)
            },
            "Quantity": 包裹数，一个包裹对应一个运单号，如果是大于1个包裹，返回则按照子母件的方式返回母运单号和子运单号
            "Commodity": [
                { "GoodsName": 商品名称 }
                ...
            ]
        }
        :return:
        失败:
        {
             "EBusinessID": "1237100",
             "ResultCode": "106",
        }
        成功:
        {
            'Order': {
                'MarkDestination': '891- 16-02 03 ',
                'PackageName': '天津转 ',
                'OrderCode': '20190710133340000000005',
                'ShipperCode': 'ZTO',
                'LogisticCode': '632589663609',
                'KDNOrderCode':
                'KDN20190710142158'
            },
            'Reason': '已接收',
            'ResultCode': '100',
            'Success': True,
            'UniquerRequestNumber': '6bc2f63d-adb2-46cd-8fb1-dacc1b20bf8b',
            'EBusinessID': 'test1542519'
        }
        """

        # 生产环境需要指定请求url
        # self.url =  PLACE_ORDER_URL
        self.request_type = PLACE_ORDER
        return self.send_request(request_data)

    def prompt_check(self, request_data):
        """
        查询快递信息
        :param request_data:
        {
            "OrderCode": 订单号（可选）,
            "ShipperCode": 物流公司代码,
            "LogisticCode": 运单号,
        }
        :return:
        {
            "ShipperCode": "SF",
            "State": "3",
            "LogisticCode": "252314540522",
            "Reason": null,
            "OrderCode": "20190406122652000000001",
            "Success": true,
            "Traces": [
                {
                    "Remark": "已经签收",
                    "AcceptTime": "2019-07-11 12:15:12",
                    "AcceptStation": "快件已经签收，签收人：张启明[武汉市]"
                },
                {
                    "Remark": "到达目的城市",
                    "AcceptTime": "2019-07-08 12:15:12",
                    "AcceptStation": "快件到达武汉市武昌区徐东大街1号网点[武汉市]"
                },
                {
                    "Remark": "离开发件城市",
                    "AcceptTime": "2019-07-07 12:15:12",
                    "AcceptStation": "快件在离开深圳集散中心，发往武汉市[深圳市]"
                },
                {
                    "Remark": null,
                    "AcceptTime": "2019-07-06 12:15:12",
                    "AcceptStation": "快件已经到达深圳集散中心[深圳市]"
                },
                {
                    "Remark": "已揽件",
                    "AcceptTime": "2019-07-05 12:15:12",
                    "AcceptStation": "深圳福田保税区网点已揽件[深圳市]"
                }
            ],
            "EBusinessID": "test1542519"
        }
        """

        # 生产环境需要指定请求url
        # self.url = PROMTE_CHECK_URL
        self.request_type = PROMPT_CHECK
        return self.send_request(request_data)
