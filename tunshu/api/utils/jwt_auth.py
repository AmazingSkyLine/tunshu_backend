import time

import jwt


def create_token(user_id):
    payload = {
        'iat': time.time(),
        'exp': time.time() + 86400 * 7,
        'sub': user_id
    }
    jwt_token = jwt.encode(payload, 'secret', algorithm='HS256')
    return jwt_token
