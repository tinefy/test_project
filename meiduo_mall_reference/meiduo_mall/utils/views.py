from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from meiduo_mall.utils.response_code import RETCODE


class LoginRequiredJSONMixin(LoginRequiredMixin):
    # def handle_no_permission(self):
    #     return JsonResponse({'code': RETCODE.SESSIONERR, 'errmsg': '用户未登录'})

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'code': RETCODE.SESSIONERR, 'errmsg': '用户未登录'})
        return super().dispatch(request, *args, **kwargs)
