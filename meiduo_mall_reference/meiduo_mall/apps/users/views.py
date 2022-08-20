import json
import logging
import re
from multiprocessing import Process

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import signing
from django.core.mail import send_mail
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse, HttpResponseBadRequest, \
    HttpResponseServerError
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.urls import reverse
from django.views import View
# from django.contrib.auth.models import User

from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.apps.verifications.views import CheckSMSCodeView
from meiduo_mall.utils.views import LoginRequiredJSONMixin
from . import constants
from .models import Address

# from meiduo_mall.apps.users.utils import UsernameMobileAuthBackend

# Create your views here.


User = get_user_model()
# 用户名：mduser
# 密码: eSJUgKnDne

logger = logging.Logger('django')


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        sms_code = request.POST.get('sms_code')
        allow = request.POST.get('allow')
        info_list = [username, password, password2, mobile, sms_code, allow]
        if not all(info_list):
            return HttpResponseForbidden('缺少必传参数！')
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return HttpResponseForbidden('请输入5-20个字符的用户名！')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseForbidden('请输入8-20位的密码！')
        if password != password2:
            return HttpResponseForbidden('两次输入的密码不一致！')

        check_sms_code_result = CheckSMSCodeView().check_sms_code(mobile, sms_code)
        if check_sms_code_result == -1:
            return render(request, 'register.html', {'sms_code_error_message': '短信验证错误！'})
        elif check_sms_code_result == -2:
            return render(request, 'register.html', {'sms_code_error_message': '短信验证过期！'})

        if allow != 'on':
            return HttpResponseForbidden('请勾选用户协议！')
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except:
            return render(request, 'register.html', {'register_errmsg': '注册失败！'})
        else:
            login(request, user)
            response = redirect(reverse('contents:index'))
            response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
            return response


class UsernameCountView(View):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        json_ = {
            'code': RETCODE.OK,
            'errmsg': 'OK',
            'count': count
        }
        return JsonResponse(json_)


class MobileCountView(View):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        json_ = {
            'code': RETCODE.OK,
            'errmsg': 'OK',
            'count': count
        }
        return JsonResponse(json_)


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        next_ = request.GET.get('next')
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')
        necessary_info_list = [username, password]
        if not all(necessary_info_list):
            return HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^[\w\d_-]{5,20}$', username):
            return HttpResponseForbidden('请输入正确的用户名或手机号')
        if not re.match(r'^[\w\d]{8,20}$', password):
            return HttpResponseForbidden('密码最少8位，最长20位')
        # user = UsernameMobileAuthBackend().authenticate(username=username, password=password)
        user = authenticate(username=username, password=password)
        if not user:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})
        login(request, user=user)
        if remembered != 'on':
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(None)
        if next_:
            response = redirect(next_)
        else:
            response = redirect(reverse('contents:index'))
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        return response


class LogoutView(View):
    def get(self, request):
        logout(request)
        response = redirect(reverse('contents:index'))
        response.delete_cookie('username')
        return response


class UserInfoView(LoginRequiredMixin, View):
    # login_url = '/login/'
    # redirect_field_name = 'redirect_to'
    def get(self, request):
        # if request.user.is_authenticated:
        #     return render(request, 'user_center_info.html')
        # else:
        #     return redirect(reverse('users:login'))
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }
        return render(request, 'user_center_info.html', context=context)


class UserInfoPasswordView(LoginRequiredJSONMixin, View):
    def get(self, request):
        context = {
            'username': request.user.username,
        }
        return render(request, 'user_center_password.html', context=context)

    def put(self, request):
        password_data_dict = json.loads(request.body.decode())
        print(password_data_dict)

        for key, value in password_data_dict.items():
            # 将key转为变量名并让key=value
            globals()[key] = value

        necessary = [old_password, new_password, new_password2]
        if not all(necessary):
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '缺少必填信息'})
        try:
            request.user.check_password(old_password)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '原密码错误'})
        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '密码最少8位，最长20位'})
        if new_password != new_password2:
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '两次输入的密码不一致'})

        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '修改密码失败'})

        user = request.user
        logout(request)
        response = JsonResponse({'code': RETCODE.OK, 'errmsg': '成功修改密码！'})
        login(request, user=user)

        # if remembered != 'on':
        #     request.session.set_expiry(0)
        # else:
        #     request.session.set_expiry(None)
        # else:
        #     response = redirect(reverse('contents:index'))
        # response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        # 清理状态保持信息
        # logout(request)
        # response = redirect(reverse('users:login'))
        # response.delete_cookie('username')

        return response


class UserEmailsView(LoginRequiredJSONMixin, View):
    def put(self, request):
        data = json.loads(request.body.decode())
        email = data['email']
        re_ = '^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$'
        if not email:
            return HttpResponseForbidden('缺少email参数')
        if not re.match(re_, email):
            return HttpResponseForbidden('参数email有误')
        try:
            # request.user.email = email
            # request.user.save()
            User.objects.filter(username=request.user.username).update(email=email)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败'})

        def generate_email_verify_url(user):
            data_ = {'user_id': user.id, 'email': email}
            token = signing.dumps(data_)
            verify_url = settings.SITE_URL + reverse('users:emails_verification') + '?token=' + token
            return verify_url

        def send_mail_():
            verify_url = generate_email_verify_url(request.user)
            subject = "美多商城邮箱验证"
            html_message = '<p>尊敬的用户您好！</p>' \
                           '<p>感谢您使用美多商城。</p>' \
                           '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                           '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)
            try:
                send_mail(subject, "", settings.EMAIL_FROM, [email], html_message=html_message)
            except Exception as e:
                logger.error(e)

        send_mail_process = Process(target=send_mail_)
        send_mail_process.start()
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})


class UserEmailsVerificationView(View):
    def get(self, request):
        token = request.GET.get('token')
        if not token:
            return HttpResponseBadRequest('缺少token')
        try:
            data_ = signing.loads(token, max_age=constants.EMAIL_VERIFICATION_CODE_EXPIRES)
        except Exception as e:
            logger.error(e)
            return HttpResponseForbidden('无效的token')
        try:
            User.objects.filter(id=data_['user_id'], email=data_['email']).update(email_active=True)
        except Exception as e:
            logger.error(e)
            return HttpResponseServerError('激活邮件失败')
        return redirect(reverse('users:info'))


class UserAddressView(LoginRequiredMixin, View):
    @staticmethod
    def address_dict(address):
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        return address_dict

    def get(self, request):
        addresses = Address.objects.filter(user=request.user, is_deleted=False)
        '''
        等同于 addresses = Address.objects.filter(user_id=request.user.id, is_deleted=False)
        SQL Query:
        SELECT `tb_address`.`id`,
               `tb_address`.`create_time`,
               `tb_address`.`update_time`,
               `tb_address`.`user_id`,
               `tb_address`.`title`,
               `tb_address`.`receiver`,
               `tb_address`.`province_id`,
               `tb_address`.`city_id`,
               `tb_address`.`district_id`,
               `tb_address`.`place`,
               `tb_address`.`mobile`,
               `tb_address`.`tel`,
               `tb_address`.`email`,
               `tb_address`.`is_deleted`
        FROM `tb_address`
        WHERE (NOT `tb_address`.`is_deleted` AND `tb_address`.`user_id` = 21)
        ORDER BY `tb_address`.`update_time` DESC LIMIT 21
        '''
        address_dict_list = []
        for address in addresses:
            address_dict_list.append(self.address_dict(address))

        def default_address_id():
            if not request.user.default_address:
                return 'null'
            else:
                return request.user.default_address.id

        context = {
            'default_address_id': default_address_id(),
            'addresses': address_dict_list,
        }
        return render(request, 'user_center_site.html', context=context)


class UserAddressCreateModifyView(LoginRequiredJSONMixin, View):
    def get_and_check_address_data_dict(self, request):
        address_data_dict = json.loads(request.body.decode())
        print(address_data_dict)

        for key, value in address_data_dict.items():
            # 将key转为变量名并让key=value
            globals()[key] = value

        error_flag = False
        # address_count = Address.objects.filter(user=request.user).count()
        # class Address 中 user = models.ForeignKey(User,..., related_name='addresses', ...)
        address_count = request.user.addresses.count()
        if address_count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            error_flag = True
            return error_flag, JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '超过地址数量上限'})

        necessary = [receiver, province_id, city_id, district_id, place, mobile]
        if not all(necessary):
            error_flag = True
            return error_flag, HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            error_flag = True
            return error_flag, HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                error_flag = True
                return error_flag, HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                error_flag = True
                return error_flag, HttpResponseForbidden('参数email有误')
        return error_flag, address_data_dict

    def get(self, request, address_id):
        try:
            address = Address.objects.get(id=address_id)
        except Exception as e:
            logger.error(e)
        else:
            address_area = {
                'address_id': address_id,
                'province_id': address.province_id,
                'city_id': address.city_id,
                'district_id': address.district_id,
            }
            return JsonResponse({'code': RETCODE.OK, 'errmsg': '获取省市id成功', 'address_area': address_area})

    def post(self, request):
        error_flag, address_data_dict = self.get_and_check_address_data_dict(request)
        if error_flag:
            return
        try:
            address = Address.objects.create(user=request.user, title=receiver, **address_data_dict)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})

        if not request.user.default_address:
            # request.user.default_address = address
            # request.user.save()
            User.objects.filter(username=request.user).update(default_address=address)

        address_dict = UserAddressView.address_dict(address)
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})

    def put(self, request, address_id):
        error_flag, address_data_dict = self.get_and_check_address_data_dict(request)
        print(address_data_dict)
        pop_needless_key = ('id', 'province', 'city', 'district')
        for item in pop_needless_key:
            address_data_dict.pop(item)
        print(address_data_dict)
        if error_flag:
            return
        try:
            Address.objects.filter(id=address_id).update(user=request.user, **address_data_dict)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '修改地址失败'})
        address = Address.objects.get(id=address_id)
        address_dict = UserAddressView.address_dict(address)
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '修改地址成功', 'address': address_dict})

    def delete(self, request, address_id):
        try:
            Address.objects.filter(id=address_id).update(is_deleted=True)
            # Address.objects.filter(id=address_id).delete()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除地址失败'})

        return JsonResponse({'code': RETCODE.OK, 'errmsg': '删除地址成功'})


class UserAddressSetDefaultView(LoginRequiredJSONMixin, View):
    def put(self, request, address_id):
        try:
            # address = Address.objects.get(id=address_id)
            # request.user.default_address = address
            # request.user.save()
            User.objects.filter(id=request.user.id).update(default_address=address_id)
        except Exception as e:
            logger.error(e)
            print(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置默认地址失败'})
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '设置默认地址成功'})


class UserAddressSetTitleView(LoginRequiredJSONMixin, View):
    def put(self, request, address_id):
        new_title_data_dict = json.loads(request.body.decode())
        new_title = new_title_data_dict['title']
        if new_title:
            try:
                # address = Address.objects.get(id=address_id)
                # request.user.default_address = address
                # request.user.save()
                Address.objects.filter(id=address_id).update(title=new_title)
            except Exception as e:
                logger.error(e)
                print(e)
                return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置地址标题失败'})
            else:
                title_dict = {'title': Address.objects.get(id=address_id).title}
                return JsonResponse({'code': RETCODE.OK, 'errmsg': '设置地址标题成功', 'title': title_dict})
        else:
            title_dict = {'title': Address.objects.get(id=address_id).title}
            return JsonResponse({'code': RETCODE.OK, 'errmsg': '新标题为空，保持原地址标题', 'title': title_dict})
