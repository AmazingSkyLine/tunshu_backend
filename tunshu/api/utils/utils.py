from django.http import JsonResponse
from django.core.files.base import ContentFile


def save_or_not(obj, data, keywords):

    # 传入参数组中的参数不为空时，保存至对象，否则略过
    for k in keywords:
        key = data.get(k, None)
        if key:
            obj.__dict__[k] = key
    obj.save()
    return obj


# 格式化响应
def json_res(status, msg, data=None):
    return JsonResponse({'msg': msg, 'data': data}, status=status)


def fetch_avatar(url, instance):
    import requests as rq
    from PIL import Image
    from io import BytesIO
    response = rq.get(url)
    im = Image.open(BytesIO(response.content))
    im_io = BytesIO()
    im.save(im_io, im.format)
    instance.avatar.save(str(instance.nickname) + '.jpg', ContentFile(im_io.getvalue()), save=False)

    return im
