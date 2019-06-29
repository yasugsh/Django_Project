# 生成美多商城公私钥命令
openssl
OpenSSL> genrsa -out app_private_key.pem 2048  # 制作私钥RSA2
OpenSSL> rsa -in app_private_key.pem -pubout -out app_public_key.pem # 导出公钥
