from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import SimpleRouter

from .views import login_views, statistical_views, users_views, goods_views


urlpatterns = [
    # rest_framework_jwt提供的登录签发JWT的视图，返回值只有token
    # url(r'^authorizations/$', obtain_jwt_token),
    url(r'^authorizations/$', login_views.AdminLoginView.as_view()),
    url(r'^users/$', users_views.UserView.as_view()),
    url(r'^goods/simple/$', goods_views.SKUViewSet.as_view({'get': 'simple'})),
    url(r'^goods/(?P<pk>\d+)/specs/$', goods_views.SKUViewSet.as_view({'get': 'specs'})),
    url(r'^goods/brands/simple/$', goods_views.SPUViewSet.as_view({'get': 'brands'})),
    url(r'^goods/channel/categories/$', goods_views.SPUViewSet.as_view({'get': 'categories'})),
    url(r'^goods/channel/categories/(?P<pk>\d+)/$', goods_views.SPUViewSet.as_view({'get': 'categories'})),
    url(r'^goods/specs/simple/$', goods_views.SpecsOptionsViewSet.as_view({'get': 'specs'})),
    url(r'^goods/channel_types/$', goods_views.GoodsChannelsViewSet.as_view({'get': 'channel_types'})),
    url(r'^goods/categories/$', goods_views.GoodsChannelsViewSet.as_view({'get': 'primary_categories'})),
]

router = SimpleRouter()
router.register(r'statistical', statistical_views.StatisticalViewSet, base_name='statistical')
router.register(r'skus', goods_views.SKUViewSet, base_name='skus')
router.register(r'goods/specs', goods_views.SpecsViewSet, base_name='goods_specs')
router.register(r'specs/options', goods_views.SpecsOptionsViewSet, base_name='specs_options')
router.register(r'goods/channels', goods_views.GoodsChannelsViewSet, base_name='channels')
router.register(r'goods', goods_views.SPUViewSet, base_name='goods')
urlpatterns += router.urls
