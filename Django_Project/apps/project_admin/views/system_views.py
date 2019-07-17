from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from project_admin.utils import PageNum
from project_admin.serializers.system_manage import PermissionSerializer, ContentTypeSerializer
from django.contrib.auth.models import Permission, ContentType


# /meiduo_admin/permission/perms/?page=1&pagesize=10&ordering=id
class PermissionViewSet(ModelViewSet):
    """用户权限管理"""
    pagination_class = PageNum

    def get_queryset(self):
        if self.action == 'content_types':
            return ContentType.objects.all()
        else:
            return Permission.objects.all()

    def get_serializer_class(self):
        if self.action == 'content_types':
            return ContentTypeSerializer
        else:
            return PermissionSerializer

    # GET /meiduo_admin/permission/content_types/
    def content_types(self, request):
        """获取权限类型列表数据"""

        content_types = self.get_queryset()
        serializer = self.get_serializer(content_types, many=True)
        return Response(serializer.data)
