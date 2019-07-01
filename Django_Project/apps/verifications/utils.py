from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from django.conf import settings


def generate_user_info_signature(user_info):
    """对用户信息进行加密"""

    # 创建加密对象
    serializer = Serializer(settings.SECRET_KEY,expires_in=600)

    # 包装数据
    data = {"user_info": user_info}

    # 对数据进行加密
    access_token = serializer.dumps(data).decode()
    return access_token


def check_user_info_signature(access_token):
    """对user信息解密"""
    # 创建加密对象
    serializer = Serializer(settings.SECRET_KEY,expires_in=600)
    try:
        # 数据进行解码
        data = serializer.loads(access_token)
    except BadData:
        return None

    # 取字典中的user_info值
    return data.get("user_info")
