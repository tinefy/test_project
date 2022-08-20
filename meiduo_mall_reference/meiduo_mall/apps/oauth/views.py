import re

from django.conf import settings
from django.contrib.auth import login, get_user_model
from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.core import signing

from meiduo_mall.apps.verifications.views import CheckSMSCodeView
from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.github_oauth import OAuthGitHub
from .models import OAuthGitHubUser

# Create your views here.
User = get_user_model()


class GitHubOAuthURLView(View):
    def get(self, request):
        next_ = request.GET.get('next')
        github = OAuthGitHub(client_id=settings.CLIENT_ID, state=next_)
        url = github.get_github_url()
        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url': url})


class GitHubOAuthView(View):
    def get(self, request):
        code = request.GET.get('code')
        next_ = request.GET.get('state')
        github = OAuthGitHub(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET,
                             code=code)
        github.get_github_access_token()
        github_user_info = github.get_github_user_info()
        openid = str(github_user_info['id'])
        try:
            oauth_user = OAuthGitHubUser.objects.get(openid=openid)
        except OAuthGitHubUser.DoesNotExist:
            access_token_openid = signing.dumps(openid)
            context = {'access_token_openid': access_token_openid}
            return render(request, 'oauth_callback.html', context)
        else:
            github_user = oauth_user.user
            login(request, github_user)
            response = redirect(next_)
            response.set_cookie('username', github_user.username, max_age=3600 * 24 * 15)
        return response

    def post(self, request):
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        sms_code = request.POST.get('sms_code')
        allow = request.POST.get('allow')
        access_token_openid = request.POST.get('access_token_openid')

        info_list = [password, password2, mobile, sms_code, allow, access_token_openid]
        if not all(info_list):
            return HttpResponseForbidden('缺少必传参数！')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseForbidden('请输入8-20位的密码！')
        if password != password2:
            return HttpResponseForbidden('两次输入的密码不一致！')

        check_sms_code_result = CheckSMSCodeView().check_sms_code(mobile, sms_code)
        if check_sms_code_result == -1:
            return render(request, 'oauth_callback.html', {'sms_code_error_message': '短信验证错误！'})
        elif check_sms_code_result == -2:
            return render(request, 'oauth_callback.html', {'sms_code_error_message': '短信验证过期！'})

        if allow != 'on':
            return HttpResponseForbidden('请勾选用户协议！')

        try:
            openid = signing.loads(access_token_openid, max_age=settings.SIGNING_MAX_AGE)
        except:
            return render(request, 'oauth_callback.html', {'openid_error_message': '无效的openid！'})

        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            user = User.objects.create_user(username=mobile, password=password, mobile=mobile)
        else:
            if not user.check_password(password):
                return render(request, 'oauth_callback.html', {'password_error_message': '绑定账户%s失败！密码错误！' % mobile})
        try:
            OAuthGitHubUser.objects.create(openid=openid, user=user)
        except DatabaseError:
            return render(request, 'oauth_callback.html', {'binding_errmsg': '绑定失败！'})

        login(request, user)
        next_ = request.GET.get('state')
        response = redirect(next_)
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        return response
