from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from datetime import date

from users.models import User


class UserTotalCountView(APIView):
    """统计总用户量"""

    # 指定管理员权限才能访问
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当前日期
        now_date = date.today()
        # 获取用户总数
        count = User.objects.all().count()
        return Response({
            'count': count,
            'date': now_date
        })
