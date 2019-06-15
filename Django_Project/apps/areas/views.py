from django.shortcuts import render
from django.views import View
import logging
from django import http

from .models import Areas
from Django_Project.utils.response_code import RETCODE, err_msg


logger = logging.getLogger('django')


class AreasView(View):
    """省市区数据"""

    def get(self, request):

        area_id = request.GET.get('area_id')

        if not area_id:
            # 前端没有传入area_id表示用户需要省份数据
            try:
                # 查询省份数据Query_Dict
                province_obj_list = Areas.objects.filter(parent__isnull=True)
                province_list = list()
                for province_obj in province_obj_list:
                    province_list.append({'id': province_obj.id, 'name': province_obj.name})
            except Exception as e:
                logger.error(e)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '省份数据错误'})

            # 响应省份数据
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})

        # 提供市 区数据
        try:
            parent_obj = Areas.objects.get(id=area_id)
            sub_obj_list = parent_obj.subs.all()

            sub_list = list()
            for sub_obj in sub_obj_list:
                sub_list.append({'id': sub_obj.id, 'name': sub_obj.name})
            sub_data = {
                'id': parent_obj.id,
                'name': parent_obj.name,
                'subs': sub_list
            }
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '城市或区数据错误'})

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})
