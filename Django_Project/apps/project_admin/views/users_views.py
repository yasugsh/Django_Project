from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.response import Response

from project_admin.serializers.users_manage import UserSerializer
from project_admin.utils import PageNum
from users.models import User


# GET&POST /meiduo_admin/users/?page=<页码>&pagesize=<页容量>&keyword=<搜索内容>
# class UserView(GenericAPIView):
#
#     pagination_class = PageNum
#     serializer_class = UserSerializer
#
#     # 重写get_queryset方法，根据前端是否传递keyword值返回不同查询集
#     def get_queryset(self):
#         keyword = self.request.query_params.get('keyword')
#         # 如果keyword是空字符，则说明要获取所有用户数据
#         if not keyword or keyword is None:
#             return User.objects.all().order_by('id')
#         else:
#             return User.objects.filter(username__contains=keyword).order_by('id')
#
#     def get(self, request):
#         queryset = self.get_queryset()
#
#         # 分页子集
#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)
#
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)


# GET&POST /meiduo_admin/users/?page=<页码>&pagesize=<页容量>&keyword=<搜索内容>
class UserView(ListCreateAPIView):
    """商城用户的查询及新增"""

    pagination_class = PageNum
    serializer_class = UserSerializer

    # 重写get_queryset方法，根据前端是否传递keyword值返回不同查询集
    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        # 如果keyword是空字符，则说明要获取所有用户数据
        if not keyword or keyword is None:
            return User.objects.all().order_by('id')
        else:
            return User.objects.filter(username__contains=keyword).order_by('id')
