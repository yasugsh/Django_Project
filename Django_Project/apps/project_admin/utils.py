from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from fdfs_client.client import Fdfs_client
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile


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


def get_fdfs_url(file):
    """
    上传文件或图片到FastDFS
    :param file: 文件或图片对象，二进制数据或本地文件
    :return: 文件或图片在FastDFS中的url
    """

    # 创建FastDFS连接对象
    fdfs_client = Fdfs_client(settings.FASTDFS_CONF_PATH)

    """
    client.upload_by_filename(文件名),
    client.upload_by_buffer(文件bytes数据)
    """
    # 上传文件或图片到fastDFS
    if isinstance(file, InMemoryUploadedFile):
        result = fdfs_client.upload_by_buffer(file.read())
    else:
        result = fdfs_client.upload_by_filename(file)
    """
    result = {
    'Group name': 'group1',  # FastDFS服务端Storage组名
    'Remote file_id': 'group1/M00/00/00/wKgThF0LMsmATQGSAAExf6lt6Ck10.jpeg',  # 文件存储的位置(索引)，可用于下载
    'Status': 'Upload successed.',  # 文件上传结果反馈
    'Local file name': '/home/python/Desktop/upload_Images/02.jpeg',  # 所上传文件的真实路径
    'Uploaded size': '76.00KB',  # 文件大小
    'Storage IP': '192.168.19.132'}  # FastDFS服务端Storage的IP
    """

    # 判断是否上传成功，result为一个字典
    if result['Status'] != 'Upload successed.':
        return Response(status=403)
    # 获取文件或图片上传后的路径
    file_url = result['Remote file_id']

    return file_url
