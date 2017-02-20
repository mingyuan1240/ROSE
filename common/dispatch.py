from django import http
import logging
logger = logging.getLogger('django.request')

def method_dispatch(**table):
    def invalid_method(request, *_, **__):
        logger.warning('Method Not Allowed (%s): %s', request.method, request.path,
                       extra={
                           'status_code': 405,
                           'request': request
                       }
        )
        return http.HttpResponseNotAllowed(table.keys())

    def dispatch(request, *args, **kwargs):
        handler = table.get(request.method, invalid_method)
        return handler(request, *args, **kwargs)
    return dispatch
