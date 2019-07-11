from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import SimpleRouter

from .views import login_views, statistical_views


urlpatterns = [
    # rest_framework_jwt提供的登录签发JWT的视图，返回值只有token
    # url(r'^authorizations/$', obtain_jwt_token),
    url(r'^authorizations/$', login_views.AdminLoginView.as_view()),
]

router = SimpleRouter()
router.register(r'statistical', statistical_views.StatisticalViewSet, base_name='statistical')
urlpatterns += router.urls
