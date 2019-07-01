from django.conf.urls import url

from . import views


# image_codes/(?P<uuid>[\w-]+)/
urlpatterns = [
    url(r'^image_codes/(?P<uuid>[\w-]+)/$', views.ImageCodeView.as_view()),
    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
    url(r'^accounts/(?P<username>[a-zA-Z0-9_-]{5,20})/sms/token/$', views.CheckImageCodeView.as_view()),
    url(r'^sms_codes/$', views.SendSMSCodeView.as_view()),
    url(r'^accounts/(?P<username>[a-zA-Z0-9_-]{5,20})/password/token/$', views.CheckSMSCodeView.as_view()),
    url(r'^users/(?P<user_id>\d+)/password/$', views.ResetPasswordView.as_view()),
]