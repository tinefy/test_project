from django.urls import re_path

# from . import views
from . import views

app_name = 'oauth'

urlpatterns = [
    re_path(r'^github/login/$', views.GitHubOAuthURLView.as_view(), name='github_login'),
    re_path(r'^oauth/$', views.GitHubOAuthView.as_view(), name='oauth'),
]
