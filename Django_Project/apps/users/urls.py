from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view()),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    # login_required装饰器判断用户是否登录(未登录将重定向到配置项中LOGIN_URL指定的地址)
    # url(r'^info/$', login_required(views.UserInfoView.as_view()), name='info'),
    url(r'^info/$', views.UserInfoView.as_view(), name='info'),
    url(r'^emails/$', views.EmailView.as_view(), name='emails'),
    url(r'^emails/verification/$', views.VerifyEmailView.as_view()),
    url(r'^addresses/$', views.AddressView.as_view(), name='addresses'),
    url(r'^addresses/create/$', views.CreateAddressView.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/$', views.UpdateDeleteAddressView.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/default/$', views.UpdateDefaultAddressView.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/title/$', views.UpdateAddressTitleView.as_view()),
    url(r'^password/$', views.ChangePasswordView.as_view()),
    url(r'^browse_histories/$', views.UserBrowseHistory.as_view()),
    url(r'^orders/info/(?P<page_num>\d+)/$', views.UserOrdersInfoView.as_view()),
    url(r'^find_password/$', views.FindPasswordView.as_view()),
]
