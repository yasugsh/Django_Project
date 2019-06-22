def get_breadcrumb(category):
    """
    通过三级类别商品查出当前的面包屑导航
    :param category: 当前选择的三级类别
    :return:
    """
    # 获取一级类别对象
    cat1 = category.parent.parent
    # 通过频道给一级类别多指定一个url
    cat1.url = cat1.goodschannel_set.all().get().url
    breadcrumb = {
        'cat1': cat1,
        'cat2': category.parent,
        'cat3': category
    }

    return breadcrumb
