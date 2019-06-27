from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^orders/settlement/$', views.OrdersSettlementView.as_view()),
    url(r'^orders/commit/$', views.OrdersCommit.as_view()),
    url(r'^orders/success/$', views.OrderSuccessView.as_view()),
]
