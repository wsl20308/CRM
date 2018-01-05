import re
from django.shortcuts import redirect,HttpResponse
from django.conf import settings

class MiddlewareMixin(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super(MiddlewareMixin, self).__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response

class LoginMiddleware(MiddlewareMixin):
    def process_request(self,request):
        if request.path_info == '/login/':
            return None
        if request.session.get('user_info'):
            return None
        return redirect('/login/')

class RbacMiddleware(MiddlewareMixin):

    def process_request(self,request):
        # 1. 获取当前请求的URL
        # request.path_info
        # 2. 获取Session中保存当前用户的权限
        # request.session.get("permission_url_list')
        current_url = request.path_info

        # 当前请求不需要执行权限验证
        for url in settings.VALID_URL:
            if re.match(url,current_url):
                return None

        permission_dict = request.session.get(settings.PERMISSION_URL_DICT_KEY)
        if not permission_dict:
            return redirect('/login/')

        flag = False
        for group_id,code_url in permission_dict.items():

            for db_url in code_url['urls']:
                regax = "^{0}$".format(db_url)
                if re.match(regax, current_url):
                    request.permission_code_list = code_url['codes']
                    flag = True
                    break
            if flag:
                break

        if not flag:
            return HttpResponse('无权访问')
