from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^orders/settlement/$', views.OrdersSettlementView.as_view()),
]
