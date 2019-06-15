from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from django.conf import settings

from . import constants


def generate_openid_signature(openid):
    """
    对openid进行签名
    :param openid: 扫码QQ的openid
    :return: 加密后的openid
    """

    serializer = Serializer(settings.SECRET_KEY, expires_in=constants.ACCESS_TOKEN_EXPIRES)
    data = {'openid': openid}
    token_openid = serializer.dumps(data)  # 对称加密(返回bytes类型)
    return token_openid.decode()


def check_openid_signature(token_openid):
    """检验token_openid"""

    serializer = Serializer(settings.SECRET_KEY, expires_in=constants.ACCESS_TOKEN_EXPIRES)
    try:
        data = serializer.loads(token_openid)
    except BadData:
        return None
    return data.get('openid')
