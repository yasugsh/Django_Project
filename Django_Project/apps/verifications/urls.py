from django.conf.urls import url

from . import views


# image_codes/(?P<uuid>[\w-]+)/
urlpatterns = [
    url(r'^image_codes/(?P<uuid>[\w-]+)/$', views.ImageCodeView.as_view()),
]