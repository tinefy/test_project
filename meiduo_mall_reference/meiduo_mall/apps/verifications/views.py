import logging
import random

from django.http import JsonResponse, HttpResponse
from django_redis import get_redis_connection
from django.views import View

from verifications.libs.captcha.captcha import captcha
from meiduo_mall.utils.response_code import RETCODE
from verifications.libs.ronglian_sms_sdk.SendMessage import CCP

from . import constants

from celery_tasks.sms.tasks import send_sms_code

# Create your views here.
logger = logging.getLogger('django')


class ImageCodeView(View):
    def get(self, request, uuid):
        text, image = captcha.generate_captcha()
        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex(f'img_{uuid}', constants.IMAGE_CODE_REDIS_EXPIRES, text)
        return HttpResponse(image, content_type='image/jpg')


class CheckImageCodeView(View):
    def get(self, request, uuid, text):
        redis_conn = get_redis_connection('verify_code')
        image_code_text = redis_conn.get(f'img_{uuid}')
        image_code_text = image_code_text.decode()
        if image_code_text.lower() == text.lower():
            return JsonResponse({'code': RETCODE.OK, 'errmsg': '图形验证码正确'})
        else:
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码错误'})


class SMSCodeView(View):
    def get(self, request, mobile):
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')
        if not all([image_code_client, uuid]):
            return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '图形验证码失效'})
        redis_conn = get_redis_connection('verify_code')
        image_code_server = redis_conn.get(f'img_{uuid}')
        image_code_server = image_code_server.decode()
        if image_code_server is None:
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码失效'})
        try:
            redis_conn.delete(f'img_{uuid}')
        except Exception as error:
            logger.error(error)
        if image_code_client.lower() != image_code_server.lower():
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '输入图形验证码有误'})
        send_flag = redis_conn.get(f'send_flag_{mobile}')
        if send_flag:
            return JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '发送短信过于频繁'})
        sms_code = '%04d' % random.randint(0, 9999)
        logger.info(sms_code)
        result = CCP().send_template_sms(mobile, (sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60), 1)
        # def send_sms(a, b, c):
        #     result = CCP().send_template_sms(a, b, c)
        #     print('Send_SMS:', b[0], result)
        # send_sms_process = Process(target=send_sms, args=(mobile, (sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60), 1))
        # send_sms_process.start()
        # #
        # send_sms_code.delay(mobile, sms_code)
        redis_pl = redis_conn.pipeline()
        redis_pl.setex(f'sms_{mobile}', constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        redis_pl.setex(f'send_flag_{mobile}', constants.SEND_SMS_CODE_INTERVAL, 1)
        redis_pl.execute()
        if result == 0:
            return JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功！'})
        else:
            return JsonResponse({'code': RETCODE.SMSCODERR, 'errmsg': '发送短信失败！'})


class CheckSMSCodeView(View):
    def get(self, request, mobile, text):
        result = self.check_sms_code(mobile, text)
        if result == 0:
            return JsonResponse({'code': RETCODE.OK, 'errmsg': '短信验证正确！'})
        elif result == -1:
            return JsonResponse({'code': RETCODE.SMSCODERR, 'errmsg': '短信验证错误！'})
        elif result == -2:
            return JsonResponse({'code': RETCODE.SMSCODERR, 'errmsg': '短信验证过期！'})

    def check_sms_code(self, mobile, text):
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get(f'sms_{mobile}')
        sms_code_server = sms_code_server.decode()
        if sms_code_server is None:
            return -2
        elif sms_code_server == text:
            return 0
        else:
            return -1
