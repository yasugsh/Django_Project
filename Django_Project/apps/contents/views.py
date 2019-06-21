from django.shortcuts import render
from django.views.generic.base import View

from .utils import get_categories
from .models import ContentCategory


# GET /
class IndexView(View):
    """首页广告"""

    def get(self, request):
        """提供首页广告页面"""

        # 获取所有商品数据
        categories = get_categories()

        """
        {
            "index_lbt": [
                {"id": 1, "title": "美图M8s", "url": "xxx", "image": "xxx"},
                {"id": 2, "title": "黑色星期五", "url": "xxx", "image": "xxx"},
                ...
            ],
            "index_kx": [
                ...
            ]
        }
        """
        # 广告数据
        contents = {}
        # 获取所有广告类型
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            # 当前广告类型下的所有上线广告
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        context = {
            'categories': categories,
            'contents': contents,
        }
        return render(request, 'index.html', context)
