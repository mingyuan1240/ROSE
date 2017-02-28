from http.client import METHOD_NOT_ALLOWED, OK, BAD_REQUEST, NOT_FOUND
import re
from common.validate import Validation
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.paginator import Paginator
from django.views import View
from django.http import JsonResponse, HttpResponse
import json
from common.validate.exceptions import ValidationError

import logging
logger = logging.getLogger('default')

class JsonView(View):
    class DictAlias(dict):
        pass
    
    validation_class = None
    NOT_FOUND = DictAlias(result=None, status_code=NOT_FOUND, message='Not Found')

    def get_json_string(self, request):
        return request.body.decode('utf-8')
    
    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() not in self.http_method_names:
            return self.http_method_not_allowed(request)

        handler = getattr(self, request.method.lower(), None)
        if handler is None:
            return self.http_method_not_allowed(request)

        # load body as json
        if request.method in ['POST', 'PUT']:
            try:
                json_string = self.get_json_string(request)
                if json_string:
                    request.json = json.loads(json_string)
                else:
                    request.json = {}
            except ValueError as e:
                logger.info('%s:%s: illegal json string: %s', request.method, request.path, e)
                ret = dict(result=None, status_code=BAD_REQUEST, message='illegal json string: %s' % e)
                return JsonResponse(ret, status=ret['status_code'])
        self.set_model(request, *args, **kwargs)
        try:
            self.validate(request, *args, **kwargs)
            result = handler(request, *args, **kwargs)
        except ValidationError as e:
            logger.info('validate error: %s', e)
            return self.handle_validate_error(request, e)
        if isinstance(result, JsonView.DictAlias):
            ret = result
        else:
            ret = JsonView.json_result(result, OK, 'ok')
        return JsonResponse(ret, status=ret['status_code'])

    def validate(self, request, *args, **kwargs):
        if self.validation_class:
            validation = self.validation_class()
            validation.validate(self.get_validate_data(request, *args, **kwargs))

    def get_validate_data(self, request, *args, **kwargs):
        return request.json

    def set_model(self, request, *args, **kwargs):
        self.model = None

    def handle_validate_error(self, request, e):
        ret = JsonView.json_result(None, BAD_REQUEST, str(e))
        return JsonResponse(ret, status=ret['status_code'])
        
    def http_method_not_allowed(self, request):
        logger.warning('Method Not Allowed (%s): %s', request.method, request.path,
                       extra={'status_code': METHOD_NOT_ALLOWED, 'request': request})
        return JsonResponse(dict(result=None, status_code=METHOD_NOT_ALLOWED, message='method not allowed: %s' % request.method), status=METHOD_NOT_ALLOWED)
    
    @staticmethod
    def json_result(result, status=OK, message=''):
        return JsonView.DictAlias(result=result, status_code=status, message=message)

class ListModelView(JsonView):
    def _is_num_str(self, s):
        return bool(re.match(r'\d+', s))
    
    def _parse_parameters(self, request):
        page = request.GET.get('page')
        if not page or not self._is_num_str(page):
            self.page = 1
        else:
            self.page = int(page)

        pagesize = request.GET.get('pageSize')
        if not pagesize or not self._is_num_str(pagesize):
            self.pagesize = 20
        else:
            self.pagesize = int(pagesize)

        orderby = request.GET.get('orderby')
        if orderby:
            orderby = orderby.replace('create_time', '-create_timestamp')
        self.orderby = orderby

    def get(self, request):
        self._parse_parameters(request)
        models = self.get_model_list(request)
        total = models.count()
        models = self.sort_model_list(models)
        models = self.paging(total, models)
        models = self.transfer_model_list(models)

        ret = dict(page=self.page, pageSize=len(models), total=total, dataList=models)
        return ret

    def paging(self, total, models):
        if (self.page - 1) * self.pagesize >= total:
            return []
        paginator = Paginator(models, self.pagesize)
        return paginator.page(self.page).object_list

    def transfer_model_list(self, models):
        return [m.brief() for m in models]

    def sort_model_list(self, models):
        if self.orderby:
            return models.order_by(self.orderby)
        return models
