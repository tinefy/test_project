from django.urls import re_path
from . import views

app_name = 'verifications'

urlpatterns = [
    re_path(r'^image_codes/(?P<uuid>[\w-]+)/$', views.ImageCodeView.as_view(), name='image_codes'),
    re_path(r'^image_codes/(?P<uuid>[\w-]+)/(?P<text>[\w\d]{4})/$', views.CheckImageCodeView.as_view(), name='image_codes_text'),
    re_path(r'^sms_code/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view(), name='sms_code'),
    re_path(r'^sms_code/(?P<mobile>1[3-9]\d{9})/(?P<text>\d{4})/$', views.CheckSMSCodeView.as_view(), name='sms_code_text'),
]
