from django.shortcuts import render
from django.views.generic.base import View
from django import http
from django.core.paginator import Paginator, EmptyPage
from django.utils import timezone

from .models import GoodsCategory, SKU, GoodsVisitCount
from contents.utils import get_categories
from .utils import get_breadcrumb
from . import constants
from Django_Project.utils.response_code import RETCODE


# GET /list/(?P<category_id>\d+)/(?P<page_num>\d+)/?sort=排序方式
class ListView(View):
    """三级类别商品列表页"""

    def get(self, request, category_id, page_num):
        """
        提供当前三级类别下的所有商品(SKU)列表页
        :param category_id: 三级类别ID
        :param page_num: 查询页码
        :return:
        """

        # 判断category_id是否正确
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseNotFound('category_id不存在')

        # 接收sort参数，默认排序方式为default
        sort = request.GET.get('sort', 'default')

        # 查询所有商品分类
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(category)

        if sort == 'price':
            # 按照价格由高到低
            sort_field = '-price'
        elif sort == 'hot':
            # 按照销量由高到低
            sort_field = '-sales'
        else:
            sort = 'default'
            sort_field = '-create_time'

        # 获取当前三级类别下的所有SKU，三级类别与SKU为一对多
        skus = SKU.objects.filter(category=category, is_launched=True).order_by(sort_field)

        # 创建分页器：每页N条记录
        paginator = Paginator(skus, constants.GOODS_LIST_LIMIT)
        # 获取列表页总页数
        total_page = paginator.num_pages
        try:
            # 获取当前页的SKU数据
            page_skus = paginator.page(page_num)
        except EmptyPage:
            # 如果page_num不正确，默认给用户404
            return http.HttpResponseNotFound('空页面')

        context = {
            'categories': categories,  # 所有商品类别
            'breadcrumb': breadcrumb,  # 面包屑导航
            'category': category,  # 第三级分类的商品
            'total_page': total_page,  # 总页数
            'page_num': page_num,  # 当前页码
            'page_skus': page_skus,  # 当前页的所有SKU数据
            'sort': sort,  # 排序字段
        }

        return render(request, 'list.html', context)


# GET hot/(?P<category_id>\d+)/
class HotGoodsView(View):
    """热销SKU排行"""

    def get(self, request, category_id):
        """
        :param category_id: 三级类别商品ID
        :return: JSON
        """

        """
        {
            "code":"0",
            "errmsg":"OK",
            "hot_skus":[
                {
                    "id":6,
                    "default_image_url":"http://image.meiduo.site:8888/group1/M00/00/02/CtM3BVrRbI2ARekNAAFZsBqChgk3141998",
                    "name":"Apple iPhone 8 Plus (A1864) 256GB 深空灰色 移动联通电信4G手机",
                    "price":"7988.00"
                },
                {
                    "id":14,
                    "default_image_url":"http://image.meiduo.site:8888/group1/M00/00/02/CtM3BVrRdMSAaDUtAAVslh9vkK04466364",
                    "name":"华为 HUAWEI P10 Plus 6GB+128GB 玫瑰金 移动联通电信4G手机 双卡双待",
                    "price":"3788.00"
                }
            ]
        }
        """

        # 查询出当前三级类别下销量前二的SKU
        skus = SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:2]

        hot_skus = []
        for sku in skus:
            hot_skus.append({
                'id': sku.id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': sku.price
            })

        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK',
            'hot_skus': hot_skus
        })


# GET /detail/(?P<sku_id>\d+)/
class DetailView(View):
    """商品详情页"""

    def get(self, request, sku_id):

        # 获取当前sku的信息
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return render(request, '404.html')

        # 查询所有商品的分类
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(sku.category)

        # 获取当前sku(16)的所有具体规格对象(颜色6：黑16, 版本7:128G21)
        current_sku_spec_qs = sku.specs.order_by('spec_id')
        # 此sku所有规格的id列表
        current_sku_option_ids = []
        for current_sku_spec in current_sku_spec_qs:
            current_sku_option_ids.append(current_sku_spec.option_id)  # [16, 21]

        # 获取当前spu下的所有sku
        temp_sku_qs = sku.spu.sku_set.all()
        spec_sku_map = {}  # 用来构造sku规格仓库
        for temp_sku in temp_sku_qs:
            # 查询所有sku的具体规格对象
            temp_spec_qs = temp_sku.specs.order_by('spec_id')
            temp_sku_option_ids = []  # 用来包装sku所有规格的id
            for temp_spec in temp_spec_qs:
                temp_sku_option_ids.append(temp_spec.option_id)
            spec_sku_map[tuple(temp_sku_option_ids)] = temp_sku.id  # {(16,20): 15, (16,21): 16}

        # 获取当前spu(3)中的所有规格对象(颜色6, 版本7)
        spu_spec_qs = sku.spu.specs.order_by('id')
        for index, spec in enumerate(spu_spec_qs):
            # 获取当前spu规格(6)中的所有选项对象
            spec_option_qs = spec.options.all()  # (13,14,15,16)
            # 复制一个新的当前sku(16)的规格id列表
            temp_option_ids = current_sku_option_ids[:]  # [16,21]
            for option in spec_option_qs:
                temp_option_ids[index] = option.id  # 13
                # 给每个spu选项对象绑定sku_id属性
                option.sku_id = spec_sku_map.get(tuple(temp_option_ids))  # sku16
            # 把spu规格下的所有选项绑定到规格对象的spec_options属性上
            spec.spec_options = spec_option_qs

        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'category': sku.category,
            'spu': sku.spu,
            'spec_qs': spu_spec_qs  # 当前spu的所有规格数据
        }

        return render(request, 'detail.html', context)


# POST /visit/(?P<category_id>\d+)/
class DetailVisitView(View):
    """详情页三级类别商品的日访问量"""

    def post(self, request, category_id):
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('无效的请求参数')

        today_date = timezone.now()  # 获取此时的日期及时间
        try:
            # 查询此类别商品当天有没有被访问过
            category_visit = GoodsVisitCount.objects.get(date=today_date, category=category)
        except GoodsVisitCount.DoesNotExist:
            # 如果没有访问过就创建一个新记录
            category_visit = GoodsVisitCount(category=category)
        category_visit.count += 1
        category_visit.save()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
