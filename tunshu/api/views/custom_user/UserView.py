import json
import logging

import jwt
import redis
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from api.utils.jwt_auth import create_token
from api.utils.serializers import book_serializer
from api.utils.utils import json_res, save_or_not, fetch_avatar
from api.utils.weixinAPIs import get_user_info
from book.models import Book
from custom_user.models import User
from tunshu import settings

logger = logging.getLogger('tunshu.views')

redis_service = redis.StrictRedis(host=settings.REDIS_HOST,
                                  port=settings.REDIS_PORT,
                                  db=settings.REDIS_DB,
                                  decode_responses=True)


@require_POST
def wx_login(request):
    """
    微信登录接口, 需要提供code, encryptedData, iv
    """
    req_data = json.loads(request.body.decode('utf-8'))
    code = req_data.get('code', None)
    encryptedData = req_data.get('encryptedData', None)
    iv = req_data.get('iv', None)

    if not code or not encryptedData or not iv:
        return json_res(400, '缺少必要参数')

    user_info = get_user_info(code, encryptedData, iv)

    openid = user_info.get('openId', 'None')
    if not openid:
        return json_res(400, '缺少参数')

    # 如果用户已绑定openid, 直接登录, 否则，自动创建新用户
    try:
        user = User.objects.get(openid=openid)
    except Exception as e:
        logger.error(e)
        user = None

    if not user:
        nickname = user_info.get('nickName', None)
        avatarUrl = user_info.get('avatarUrl', None)

        try:
            user = User.objects.create(
                nickname=nickname, openid=openid)
            
            fetch_avatar(avatarUrl, user)
            user.save()
        except Exception as e:
            logger.error(e)
            return json_res(400, '用户创建失败')

    jwt_token = create_token(user.id)
    data = {'jwt_token': jwt_token, 'user_id': user.id,
            'detail_url': 'http://139.199.131.21/api/user/{}/'.format(user.id),
            'avatarUrl': 'http://139.199.131.21' + user.avatar.url,
            'nickname': user.nickname}

    return json_res(200, '登录成功', data)


def user_info(request, user_id):

    user = get_object_or_404(User, id=user_id)
    res_dict = {
        'id': user.id,
        'nickname': user.nickname,
        'major': user.major,
        'avatarUrl': 'http://139.199.131.21' + user.avatar.url
    }

    return json_res(200, '获取用户信息成功', res_dict)


def change_user_info(request):
    req_data = json.loads(request.body.decode('utf-8'))
    user = request.custom_user

    try:
        save_or_not(user, req_data, ['nickname', 'major', 'weixin', 'phone'])
    except Exception as e:
        logger.error(e)
        return json_res(400, '更新用户信息失败')

    return json_res(200, '更新用户信息成功')


def get_user_books(request):

    books = Book.objects.filter(owner=request.custom_user)

    res_dict = book_serializer(books)
    return json_res(200, '获取用户书架成功', res_dict)


def user_auth(request):
    jwt_token = request.META.get('HTTP_AUTHORIZATION', None)
    try:
        data = jwt.decode(jwt_token, 'secret', algorithm='HS256')
    except Exception as e:
        logger.error(e, jwt_token)
        return json_res(403, '认证失败')

    # if get token then user must exist
    try:
        user = User.objects.get(id=data['sub'])
    except Exception as e:
        logger.error(e)
        return json_res(403, '用户不存在')

    return json_res(200, 'Confirmed')