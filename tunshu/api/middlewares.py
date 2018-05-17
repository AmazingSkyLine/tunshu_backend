from custom_user.models import User
from tunshu.settings import NEED_AUTH_URL, POST_NEED_AUTH_URL
from django.utils.deprecation import MiddlewareMixin
import re
import logging
import jwt
from api.utils.utils import json_res

need_auth_path = [re.compile(item) for item in NEED_AUTH_URL]
post_need_auth_path = [re.compile(item) for item in POST_NEED_AUTH_URL]

logger = logging.getLogger('tunshu.views')


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # check if url is in lists_need_to_auth
        url_path = request.path

        is_need_auth = 0
        for each in need_auth_path:
            if re.fullmatch(each, url_path):
                is_need_auth = 1
                break

        if not is_need_auth:
            # if already need auth, skip this check
            if request.method != 'GET':
                for each in post_need_auth_path:
                    if re.fullmatch(each, url_path):
                        is_need_auth = 1
                        break

        if is_need_auth:
            # if authenticated, add custom_user to request
            jwt_token = request.META.get('HTTP_AUTHORIZATION', None)
            try:
                data = jwt.decode(jwt_token, 'secret', algorithm='HS256')
            except Exception as e:
                logger.error(jwt_token, error=e)
                return json_res(403, '认证失败')

            # if get token then user must exist
            try:
                user = User.objects.get(id=data['sub'])
            except Exception as e:
                logger.error(e)
                return json_res(404, '用户不存在')
            request.custom_user = user
