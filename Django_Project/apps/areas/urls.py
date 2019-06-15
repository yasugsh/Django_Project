from django.contrib.auth.urls import url

from . import views


urlpatterns = [
    url(r'^areas/$', views.AreasView.as_view()),
]
