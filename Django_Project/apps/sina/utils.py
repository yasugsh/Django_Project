from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,BadData
from django.contrib.auth import settings


def generate_uid_signature(uid):
    """对uid进行加密"""

    # 创建加密对象
    serializer = Serializer(settings.SECRET_KEY, expires_in=600)

    # 包装数据
    data = {"uid": uid}

    # 对数据进行加密
    sign_uid = serializer.dumps(data).decode()
    return sign_uid


def check_uid_signature(sign_uid):
    """对uid解密"""
    # 创建加密对象
    serializer = Serializer(settings.SECRET_KEY,expires_in=600)
    try:
        # 数据进行解码
        data = serializer.loads(sign_uid)
    except BadData:
        return None

    # 取字典中的uid值
    return data.get("uid")
