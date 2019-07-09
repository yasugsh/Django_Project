def jwt_response_payload_handler(token, user=None, request=None):
    """自定义jwt认证成功后返回的数据，
    在DRF JWT生成token的视图返回值中增加username和user_id"""

    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }
