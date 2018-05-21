from weixin import WXAPPAPI
from weixin.lib.wxcrypt import WXBizDataCrypt

from custom_user.models import User

WXAPP_APPID = ''
WXAPP_SECRET = ''

api = WXAPPAPI(appid=WXAPP_APPID, app_secret=WXAPP_SECRET)


def get_user_info(code, encryptedData, iv):
    # wx.login()接口success方法获得的响应，将响应中的code发送至第三方服务器，第三方服务器
    # 访问微信接口，获取session_key
    session_info = api.exchange_code_for_session_key(code=code)
    session_key = session_info.get('session_key')

    crypt = WXBizDataCrypt(WXAPP_APPID, session_key)

    # encryptedData 包含用户完整信息的加密数据
    # iv 加密算法的初始向量

    # 返回用户完整信息
    user_info = crypt.decrypt(encryptedData, iv)
    return user_info


def verify_wx(encryptedData, iv, code):
    user_info = get_user_info(encryptedData, iv, code)
    openid = user_info.get('openId', 'None')
    if openid:
        auth = User.objects.filter(openid=openid)
        if not auth:
            return 401
        return auth
    return 403


def get_openid(code):
    session_info = api.exchange_code_for_session_key(code=code)
    return session_info['openid']
