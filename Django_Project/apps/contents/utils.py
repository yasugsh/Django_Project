from goods.models import GoodsChannel


def get_categories():
    """查询商品频道和分类数据"""

    """
    {
        "1": {
            "channels": [
                {"id": 1, "name": "手机", "url": "xxx"},
                {"id": 2, "name": "相机", "url": "xxx"}
            ],
            "sub_cats": [
                {
                    "id": 38,
                    "name": "手机通讯",
                    "sub_cats": [
                        {"id": 115, "name": "手机"},
                        {"id": 116, "name": "游戏手机"}
                    ]
                },
                {
                    "id": 39,
                    "name": "手机配件",
                    "sub_cats": [
                        {"id": 119, "name": "手机壳"},
                        {"id": 120, "name": "贴膜"}
                    ]
                }
            ]
        },
        "2": {
            "channels": [],
            "sub_cats": []
        }
    }
    """

    categories = {}  # 用来包装所有商品类别数据大字典
    # 获取所有频道数据(37个)
    goods_channels_qs = GoodsChannel.objects.order_by('group_id', 'sequence')

    for channel in goods_channels_qs:
        group_id = channel.group_id  # 获取频道组号

        # 判断当前组号是否在大字典中
        if group_id not in categories:
            # 不存在,包装一个当前组的准备数据
            categories[group_id] = {
                'channels': [],
                'sub_cats': []
            }

        cat1 = channel.category  # 通过频道的外键获取一级类别数据
        cat1.url = channel.url  # 将频道的url绑定给一级类型对象
        categories[group_id]['channels'].append(cat1)

        cat2_qs = cat1.subs.all()  # 获取当前一级类型下所有二级数据
        for cat2 in cat2_qs:
            cat3_qs = cat2.subs.all()  # 获取当前二级类型下所有三级数据
            cat2.sub_cats = cat3_qs  # 把二级下的所有三级绑定给cat2对象的sub_cats属性
            categories[group_id]['sub_cats'].append(cat2)

    return categories
