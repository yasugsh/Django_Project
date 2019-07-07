from django.contrib.auth.urls import url

from . import views, generic_api_views, generic_view_set


urlpatterns = [
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', views.ListView.as_view()),
    url(r'^hot/(?P<category_id>\d+)/$', views.HotGoodsView.as_view()),
    url(r'^detail/(?P<sku_id>\d+)/$', views.DetailView.as_view()),
    url(r'^visit/(?P<category_id>\d+)/$', views.DetailVisitView.as_view()),
    url(r'^comments/(?P<sku_id>\d+)/$', views.CommentsView.as_view()),
    url(r'^goods/$', generic_api_views.GoodsListView.as_view()),
    url(r'^goods/(?P<pk>\d+)/$', generic_api_views.GoodsDetailView.as_view()),
    url(r'^goods_set/$', generic_view_set.GoodsViewSet.as_view({'get': 'list'})),
]
