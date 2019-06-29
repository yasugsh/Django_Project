from django.contrib.auth.urls import url

from . import views


urlpatterns = [
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', views.ListView.as_view()),
    url(r'^hot/(?P<category_id>\d+)/$', views.HotGoodsView.as_view()),
    url(r'^detail/(?P<sku_id>\d+)/$', views.DetailView.as_view()),
    url(r'^visit/(?P<category_id>\d+)/$', views.DetailVisitView.as_view()),
    url(r'^comments/(?P<sku_id>\d+)/$', views.CommentsView.as_view()),
]
