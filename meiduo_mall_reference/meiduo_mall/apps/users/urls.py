from django.urls import re_path
from . import views

app_name = 'users'

urlpatterns = [
    re_path(r'^register/$', views.RegisterView.as_view(), name='register'),
    re_path(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view(),
            name='usernames'),
    re_path(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view(), name='mobiles'),
    re_path(r'^login/$', views.LoginView.as_view(), name='login'),
    re_path(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    re_path(r'^info/$', views.UserInfoView.as_view(), name='info'),
    re_path(r'^info/password/$', views.UserInfoPasswordView.as_view(), name='password'),
    re_path(r'^emails/$', views.UserEmailsView.as_view(), name='emails'),
    re_path(r'^emails/verification/$', views.UserEmailsVerificationView.as_view(), name='emails_verification'),
    re_path(r'^address/$', views.UserAddressView.as_view(), name='address'),
    re_path(r'^address/create/$', views.UserAddressCreateModifyView.as_view(), name='address_create'),
    re_path(r'^address/(?P<address_id>\d+)/area/$', views.UserAddressCreateModifyView.as_view(),
            name='address_area'),
    re_path(r'^address/(?P<address_id>\d+)/modify/$', views.UserAddressCreateModifyView.as_view(),
            name='address_modify'),
    re_path(r'^address/(?P<address_id>\d+)/delete/$', views.UserAddressCreateModifyView.as_view(),
            name='address_delete'),
    re_path(r'^address/(?P<address_id>\d+)/set/default/$', views.UserAddressSetDefaultView.as_view(),
            name='address_set_default'),
    re_path(r'^address/(?P<address_id>\d+)/set/title/$', views.UserAddressSetTitleView.as_view(),
            name='address_set_default'),
]
