# coding: utf-8

from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from ac_api import views

router = DefaultRouter()
router.register(r'user/results', views.UserResultsApi, base_name='user')


urlpatterns = [
    url(r'^computing/$', views.ComputingComputeApi.as_view()),
    url(r'^computing/polling/$', views.ComputingPollingApi.as_view()),
    url(r'^categories/(?P<categoryName>\w+)/$', views.CategoryView.as_view(), name='categories'),
    url(r'^user/auctions/$', views.UserAuctionsApi.as_view()),
    url(r'^user/data/$', views.UserDataApi.as_view()),
    url(r'^user/login/$', views.UserLoginApi.as_view()),
    url(r'^user/login/(?P<source>(facebook)?)/$', views.UserLoginApi.as_view()),
    url(r'^user/logout/$', views.UserLogoutApi.as_view()),
    url(r'^user/register/$', views.UserRegisterApi.as_view()),
    url(r'^user/password/$', views.UserPasswordChangeApi.as_view()),
    url(r'^user/password/reset/$', views.UserPasswordResetApi.as_view()),
    url(r'^user/password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>\w+)/$', views.UserPasswordResetUrlApi.as_view()),
    url(r'^user/triggers/$', views.UserTriggersApi.as_view()),
    url(r'^user/triggers/(?P<trigger_id>[0-9]+)/$', views.UserTriggersApi.as_view()),
    url(r'^user/triggers/(?P<trigger_id>[0-9]+)/export/$', views.UserTriggersApi.as_view()),
]

urlpatterns += router.urls