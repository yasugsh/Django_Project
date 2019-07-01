from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^sina/login/$', views.SinaLoginUrlView.as_view()),
    url(r'^sina_callback/$', views.SinaCallbackView.as_view()),
    url(r'^oauth/sina/user/$', views.SinaAuthUserView.as_view()),
]
