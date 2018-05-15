import json
import logging
import random

import redis
import requests
from django.shortcuts import get_object_or_404

from api.utils.jwt_auth import create_token
from api.utils.serializers import book_serializer, NotificationSerializer
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
        gender = user_info.get('gender', None)
        avatarUrl = user_info.get('avatarUrl', None)

        try:
            user = User.objects.create(
                nickname=nickname, gender=gender,
                openid=openid)
            
            fetch_avatar(avatarUrl, user)
            user.save()
        except Exception as e:
            logger.error(e)
            return json_res(400, '用户创建失败')

    jwt_token = str(create_token(user.id))[2:-1]
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
        'gender': user.gender,
        'major': user.major,
        'avatarUrl': 'http://139.199.131.21' + user.avatar.url
    }

    return json_res(200, '获取用户信息成功', res_dict)


def get_user_social(request):
    try:
        user = request.custom_user
    except Exception as e:
        logger.error(e)
        return json_res(403, '未登录')
    return json_res(200, '获取用户联系方式成功', {'qq': user.qq, 'weixin': user.weixin})


def change_user_info(request):
    req_data = json.loads(request.body.decode('utf-8'))
    user = request.custom_user

    try:
        save_or_not(user, req_data, ['nickname', 'gender', 'major', 'qq', 'weixin', 'phone'])
    except Exception as e:
        logger.error(e)
        return json_res(400, '更新用户信息失败')

    return json_res(200, '更新用户信息成功')


def send_code(request):
    phone = request.GET.get('phone', None)
    if not phone:
        return json_res(400, '缺少参数')

    # 生成验证码并保存至redis
    validate_code = ''
    for i in range(6):
        validate_code += str(random.randint(0, 9))

    redis_service.set(phone, validate_code, ex=60)

    api_url = 'http://v.juhe.cn/sms/send'
    app_key = 'dc192fa7c88ab7062dbd981187fd20a9'
    payload = {'mobile': phone, 'tpl_id': 66702,
               'tpl_value': '#code#=%s' % validate_code,
               'key': app_key}
    r = requests.get(api_url, params=payload)
    if r.json().get('result'):
        return json_res(200, '验证码发送成功')
    else:
        return json_res(400, '验证码发送失败')


def get_user_books(request):

    books = Book.objects.filter(owner=request.custom_user)

    res_dict = book_serializer(books)
    return json_res(200, '获取用户书架成功', res_dict)


def show_user_sent_notify(request):
    user = request.custom_user

    res_data = NotificationSerializer(user.sent_notify, many=True).data

    return json_res(200, '获取用户发送信息成功', res_data)


def show_user_received_notify(request):
    user = request.custom_user

    res_data = NotificationSerializer(user.received_notify, many=True).data

    return json_res(200, '获取用户接收信息成功', res_data)
