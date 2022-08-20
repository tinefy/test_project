from django.urls import re_path

from . import views

app_name = 'areas'

urlpatterns = [
    re_path(r'^areas/$', views.AreasView.as_view(), name='areas'),
]
