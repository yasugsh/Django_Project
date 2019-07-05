from django.shortcuts import render
from django.template import loader
from django.conf import settings
import time, os

from .utils import get_categories
from .models import ContentCategory


def generate_static_index_html():
    """生成静态的主页html"""

    # Sat Jun 29 18:52:11 2019: generate_static_html
    print('%s: generate_static_html' % time.ctime())

    # 获取商品频道和分类
    categories = get_categories()

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

    # # 获取首页模板文件
    template = loader.get_template('index.html')
    # 获取出的真实数据都渲染到首页html字符串
    html_text = template.render(context)

    # html_text = render(None, 'index.html', context).content.decode()

    """
    将首页html字符串写入到指定目录下的index.html文件中，
    python -m http.server 8080 --bind 127.0.0.1 开启测试静态服务器，
    通过 http://127.0.0.1:8080/static/index.html 访问此静态文件
    """
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'index.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)
