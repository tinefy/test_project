from django.db import models

# Create your models here.
from meiduo_mall.utils.models import BaseModel


class OAuthGitHubUser(BaseModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    openid = models.CharField(max_length=64, db_index=True, verbose_name='GitHubID')
    githubdata = models.JSONField(null=True)

    class Meta(object):
        db_table = 'tb_oauth_github'
        verbose_name = 'GitHub登录用户数据'
        verbose_name_plural = verbose_name
