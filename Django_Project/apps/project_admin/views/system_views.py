from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from project_admin.utils import PageNum
from project_admin.serializers.system_manage import PermissionSerializer, ContentTypeSerializer, \
    GroupSerializer, OperateUserSerializer
from django.contrib.auth.models import Permission, ContentType, Group
from users.models import User


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


# /meiduo_admin/permission/groups/
class GroupViewSet(ModelViewSet):
    """用户组管理"""
    pagination_class = PageNum

    def get_queryset(self):
        if self.action == 'perms_simple':
            return Permission.objects.all().order_by('id')
        else:
            return Group.objects.all().order_by('id')

    def get_serializer_class(self):
        if self.action == 'perms_simple':
            return PermissionSerializer
        else:
            return GroupSerializer

    # GET/meiduo_admin/permission/simple/
    def perms_simple(self, request):
        """获取权限表数据"""

        permissions = self.get_queryset()
        serializer = self.get_serializer(permissions, many=True)
        return Response(serializer.data)


# /meiduo_admin/permission/admins/
class OperateUserViewSet(ModelViewSet):
    """运营用户管理"""
    pagination_class = PageNum

    def get_queryset(self):
        if self.action == 'simple':
            return Group.objects.all().order_by('id')
        else:
            return User.objects.filter(is_staff=True).order_by('id')

    def get_serializer_class(self):
        if self.action == 'simple':
            return GroupSerializer
        else:
            return OperateUserSerializer

    # GET /meiduo_admin/permission/groups/simple/
    def simple(self, request):
        """获取用户分组表"""

        groups = self.get_queryset()
        serializer = self.get_serializer(groups, many=True)
        return Response(serializer.data)
