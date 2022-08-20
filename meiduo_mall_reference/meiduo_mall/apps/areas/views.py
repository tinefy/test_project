import logging

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

# Create your views here.
from .models import Area
from meiduo_mall.utils.response_code import RETCODE

logger = logging.Logger('django')


class AreasView(View):
    def get(self, request):
        area_id = request.GET.get('area_id')
        if not area_id:
            # 如果area_id为空，则请求省数据
            try:
                province_model_list = Area.objects.filter(parent__isnull=True)
            except Exception as e:
                logger.error(e)
                return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '省份数据错误'})
            else:
                province_list = []
                for province_model in province_model_list:
                    province_list.append({'id': province_model.id, 'name': province_model.name})
                return JsonResponse(
                    {
                        'code': RETCODE.OK,
                        'errmsg': 'OK',
                        'province_list': province_list
                    }
                )
        else:
            # 如果area_id非空，则请求市/区数据
            try:
                province_model = Area.objects.get(id__exact=area_id)
                # sub_model_list = Area.objects.filter(parent__exact=area_id)
                sub_model_list = province_model.subs.all()
            except Exception as e:
                logger.error(e)
                return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '市/区数据错误'})
            else:
                subs = []
                for sub_model in sub_model_list:
                    subs.append({'id': sub_model.id, 'name': sub_model.name})
                return JsonResponse(
                    {
                        'code': RETCODE.OK,
                        'errmsg': 'OK',
                        'sub_data': {
                            'id': province_model.id,
                            'name': province_model.name,
                            'subs': subs,
                        },
                    }
                )
