from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PageNum(PageNumberPagination):
    """自定义页面分页器"""

    page_size = 5  # 后端指定页容量
    page_size_query_param = 'pagesize'  # 前端传递页容量的关键字，默认为None
    max_page_size = 10  # 前端最多能设置的页容量
    page_query_param = 'page'  # 前端传递页码的关键字，默认为page

    # 重写分页返回方法，按照指定的字段进行分页数据返回
    def get_paginated_response(self, data):
        """
        自定义返回的数据格式
        :param data: 分页子集序列化的结果
        :return: 具有自定义数据格式的相应对象
        """

        # paginator = self.django_paginator_class(queryset, page_size)
        return Response({
            'count': self.page.paginator.count,  # 数据总数量
            'lists': data,  # 序列化后的数据子集
            'page': self.page.number,  # 当前页码
            'pages': self.page.paginator.num_pages,  # 总页数
            'pagesize': self.page_size  # 后端指定的页容量
        })
