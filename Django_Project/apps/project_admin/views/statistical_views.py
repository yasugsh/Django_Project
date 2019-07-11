from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from django.utils import timezone
from rest_framework.response import Response
import pytz
from  django.conf import settings
from datetime import timedelta

from users.models import User
from orders.models import OrderInfo
from goods.models import GoodsVisitCount
from project_admin.serializers.statistical import GoodsSerializer


class StatisticalViewSet(ViewSet):

    permission_classes = [IsAdminUser]

    # GET /meiduo_admin/statistical/total_count/
    @action(methods=['get'], detail=False)
    def total_count(self, request):
        """统计总用户量"""

        # 获取当前日期 '2019-07-09'
        today_date = timezone.now().date()
        # 获取用户总数
        count = User.objects.count()
        return Response({
            'count': count,
            'date': today_date
        })

    # GET /meiduo_admin/statistical/day_increment/
    @action(methods=['get'], detail=False)
    def day_increment(self, request):
        """每日新增用户量统计"""

        # 获取当前日期(东八区)0时时间点
        # timezone.now()当前时刻的UTC时间;
        # pytz.timezone(settings.TIME_ZONE)当前服务器所在的本地时区对象;
        # astimezone将UTC时间转换为本地时区时间
        today_date_start = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE)).replace(hour=0, minute=0, second=0)

        # date_joined 记录用户创建账户的UTC时间，进行对比时自动转换为本地时区
        count = User.objects.filter(date_joined__gte=today_date_start).count()
        return Response({
            'count': count,
            'date': today_date_start.date()
        })

    # GET /meiduo_admin/statistical/day_active/
    @action(methods=['get'], detail=False)
    def day_active(self, request):
        """每日活跃用户量统计"""

        # 获取当前日期(东八区)0时
        today_date_start = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE)).replace(hour=0, minute=0, second=0)
        # last_login 记录用户最后一次登录的时间
        count = User.objects.filter(last_login__gte=today_date_start).count()
        return Response({
            'count': count,
            'date': today_date_start.date()
        })

    # GET /meiduo_admin/statistical/day_orders/
    @action(methods=['get'], detail=False)
    def day_orders(self, request):
        """每日下单的用户量"""

        # 获取当前日期(东八区)0时
        today_date_start = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE)).replace(hour=0, minute=0, second=0)

        # 1、从订单表查询出下单的用户量
        # today_orders = OrderInfo.objects.filter(create_time__gte=now_date_start)
        #
        # user_id_list = []
        # for order in today_orders:
        #     user_id_list.append(order.user_id)
        # count = len(set(user_id_list))

        # 2、直接查询用户表，关联过滤查询 orderinfo相当于related_name='orders'
        today_order_users = User.objects.filter(orderinfo__create_time__gte=today_date_start)
        count = len(set(today_order_users))

        return Response({
            'count': count,
            'date': today_date_start.date()
        })

    # GET /meiduo_admin/statistical/month_increment/
    @action(methods=['get'], detail=False)
    def month_increment(self, request):
        """月增用户量统计"""

        today_date = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))
        # 获取一个月前日期、timedelta(29)表示一个时间段
        start_date = today_date - timedelta(days=29)

        date_list = []
        for i in range(30):
            # 循环遍历获取第i天日期的零点
            index_date_start = (start_date + timedelta(days=i)).replace(hour=0, minute=0, second=0)
            # 指定下一天的零点
            next_date_start = start_date + timedelta(days=i + 1)
            # 查询注册时间大于index_date，小于next_date的用户，得到第i天用户量
            count = User.objects.filter(date_joined__gte=index_date_start, date_joined__lt=next_date_start).count()

            date_list.append({
                'date': index_date_start.date(),
                'count': count
            })

        return Response(date_list)

    # GET /meiduo_admin/statistical/goods_day_views/
    @action(methods=['get'], detail=False)
    def goods_day_views(self, request):
        """三级分类商品的日访问量"""

        today_date = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))
        # 获取当天访问的商品分类数量信息
        good_visit = GoodsVisitCount.objects.filter(date=today_date)
        serializer = GoodsSerializer(instance=good_visit, many=True)

        return Response(serializer.data)
