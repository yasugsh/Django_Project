"""
Django settings for Django_Project project.

Generated by 'django-admin startproject' using Django 1.11.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
import datetime
import os, sys
import djcelery

"""
print(sys.path)
['/home/python/Desktop/self_code/Phase_new/Django_Project',  # pycharm自动解释生成的当前项目导包根路径
 '/home/python/Desktop/self_code/Phase_new/Django_Project',  # 当前项目的导包根路径
 '/snap/pycharm-professional/136/helpers/pycharm_display', 
 '/home/python/.virtualenvs/py3_django/lib/python36.zip', 
 '/home/python/.virtualenvs/py3_django/lib/python3.6', 
 '/home/python/.virtualenvs/py3_django/lib/python3.6/lib-dynload', 
 '/usr/lib/python3.6', 
 '/home/python/.virtualenvs/py3_django/lib/python3.6/site-packages', 
 '/snap/pycharm-professional/136/helpers/pycharm_matplotlib_backend']
 """

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# /home/python/Desktop/self_code/Phase_new/Django_Project/Django_Project/apps
sys.path.insert(0, os.path.join(BASE_DIR, "apps"))  # 添加导包路径到当前环境下的导包路径列表中

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'dy+=e*-@dd)6!*mg+$ze#3%9kub&w2nj#znj09qwkr%q77&7gp'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']  # 允许访问本服务器的域名(默认127.0.0.1)


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'haystack',  # 通过Haystack框架来调用Elasticsearch搜索引擎
    'django_crontab', # 定时任务
    'rest_framework',
    'corsheaders',  # django-cors-headers拓展解决跨域
    'werkzeug_debugger_runserver',
    'django_extensions',
    'djcelery',  # djcelery实现快递下单接口的异步任务

    # 'users',  # 使用基类AppConfig中的相关配置
    'users.apps.UsersConfig',  # 使用自定义配置类users.apps中的配置
    'contents.apps.ContentsConfig',
    'verifications.apps.VerificationsConfig',
    'oauth.apps.OauthConfig',
    'areas.apps.AreasConfig',
    'goods.apps.GoodsConfig',
    'orders.apps.OrdersConfig',
    'payment.apps.PaymentConfig',
    'sina.apps.SinaConfig',
    'project_admin.apps.ProjectAdminConfig'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # 必须放第一位置
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Django_Project.urls'

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]

# 配置Jinja2模板引擎
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',  # jinja2模板引擎
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # 引入Jinja2模板引擎环境
            'environment': 'Django_Project.utils.jinja2_env.jinja2_environment',
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',  # Django自带模板
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Django_Project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

DATABASES = {
    'default': {  # 主机(写)
        'ENGINE': 'django.db.backends.mysql',  # 数据库引擎
        'HOST': '192.168.246.128',  # 数据库主机
        'PORT': 3306,  # 数据库端口
        'USER': 'yin',  # 数据库用户名
        'PASSWORD': 'mysql',  # 数据库用户密码
        'NAME': 'Django_Project'  # 数据库名字
    },
    'slave': {  # 从机(读)
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '192.168.246.128',
        'PORT': 3307,
        'USER': 'root',
        'PASSWORD': 'mysql',
        'NAME': 'Django_Project'
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

# LANGUAGE_CODE = 'en-us'
# TIME_ZONE = 'UTC'

# 语言(显示中文)
LANGUAGE_CODE = 'zh-hans'
# 时区
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

# 为True 数据库时区还是UTC
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

# 存放查找静态文件的目录 接收的是list
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# 图片上传后保存的文件夹
MEDIA_ROOT=os.path.join(BASE_DIR, "static/images")

"""
session默认的存储方式，数据库中
SESSION_ENGINE='django.contrib.sessions.backends.db'

存储在本机内存中，如果丢失则不能找回
SESSION_ENGINE='django.contrib.sessions.backends.cache'

混合存储，优先从本机内存中存取，如果没有则从数据库中存取
SESSION_ENGINE='django.contrib.sessions.backends.cached_db'
"""

# 配置redis数据库
CACHES = {
    "default": {
        # 后端RedisCache
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.246.128:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": "myredis",  # requirepass:myredis
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
            "DECODE_RESPONSES": True
        }
    },
    "session": {  # session缓存
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.246.128:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": "myredis",  # requirepass:myredis
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
            "DECODE_RESPONSES": True
        }
    },
    "verify_code": {  # 图形验证码
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.246.128:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": "myredis",
        }
    },
    "history": {  # 用户浏览记录
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.246.128:6379/3",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": "myredis",
        }
    },
    "carts": {  # 登录用户购物车数据
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.246.128:6379/4",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": "myredis",
        }
    },
}

# 设置将session存储到redis中
SESSION_ENGINE = "django.contrib.sessions.backends.cache"  # 指定session的存储方式(内存)
SESSION_CACHE_ALIAS = "session"  # 指定session储存位置

# 日志输出器配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'formatters': {  # 日志信息显示的格式
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {  # 对日志进行过滤
        'require_debug_true': {  # django在debug模式下才输出日志
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {  # 日志处理方法
        'console': {  # 向终端中输出日志
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {  # 向文件中输出日志
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), 'logs/project.log'),  # 日志文件的位置
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {  # 日志器
        'django': {  # 定义了一个名为django的日志器
            'handlers': ['console', 'file'],  # 可以同时向终端与文件中输出日志
            'propagate': True,  # 是否继续传递日志信息
            'level': 'INFO',  # 日志器接收的最低日志级别
        },
    }
}

# (修改)指定本项目使用的用户模型类
AUTH_USER_MODEL = 'users.User'

# 指定自定义的用户认证后端(实现多账号登录)
AUTHENTICATION_BACKENDS = ['Django_Project.utils.authenticate.UserAuthenticateBackend']

# 用户在未登录的状态下访问用户中心将被重定向到此url
LOGIN_URL = '/login/'

# QQ登录参数
QQ_CLIENT_ID = '101568493'
QQ_CLIENT_SECRET = 'e85ad1fa847b5b79d07e40f8f876b211'
QQ_REDIRECT_URI = 'http://www.meiduo.site:8000/oauth_callback'

# 准备发邮件方法send_email()的参数
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # 指定邮件后端
EMAIL_HOST = 'smtp.163.com'  # 发邮件主机
EMAIL_PORT = 25  # 发邮件端口
EMAIL_HOST_USER = 'yq976093462@163.com'  # 授权的邮箱
EMAIL_HOST_PASSWORD = '567cnmbdwy163'  # 邮箱授权时获得的密码，非注册登录密码
EMAIL_FROM = '<yq976093462@163.com>'  # 发件人抬头
EMAIL_VERIFY_URL = 'http://www.meiduo.site:8000/emails/verification/'

# 指定自定义的Django文件存储类
DEFAULT_FILE_STORAGE = 'Django_Project.utils.fastdfs.fdfs_storage.FastDFSStorage'

# FastDFS相关参数
# FDFS_BASE_URL = 'http://192.168.19.132:8888/'
FDFS_BASE_URL = 'http://image.meiduo.site:8888/'

# 指定连接FastDFS服务器的配置文件
# FASTDFS_CONF_PATH = 'Django_Project/utils/fastdfs/client.conf'  # 相对路径
FASTDFS_CONF_PATH = os.path.join(BASE_DIR, 'utils/fastdfs/client.conf')  # 绝对路径

# 将Haystack配置为搜索引擎后端
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://192.168.246.128:9200', # Elasticsearch服务器ip地址，端口号固定为9200
        'INDEX_NAME': 'django', # 在Elasticsearch建立的索引库的名称
    },
}

# 当添加、修改、删除数据时，自动生成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
# 查询出的数据每页显示条数，haystack.views中已设置默认为20条
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 5

# 支付宝测试账号
"""
账号：wexohi8786@sandbox.com
密码：111111
"""
ALIPAY_APPID = '2016101100657905'
ALIPAY_DEBUG = True  # 表示是沙箱环境还是真实支付环境
ALIPAY_URL = 'https://openapi.alipaydev.com/gateway.do'  # 支付宝(沙箱环境)网关
ALIPAY_RETURN_URL = 'http://www.meiduo.site:8000/payment/status/'  # 回调地址

# 微博登录参数
SINA_CLIENT_KEY = '3305669385'
SINA_CLIENT_SECRET = '74c7bea69d5fc64f5c3b80c802325276'
SINA_REDIRECT_URL = 'http://www.meiduo.site:8000/sina_callback'


CRONJOBS = [
    # 每1分钟生成一次首页静态文件,指定log输出文件
    ('*/1 * * * *', 'contents.crons.generate_static_index_html', '>> ' + os.path.join(os.path.dirname(BASE_DIR), 'logs/crontab.log'))
]

# 解决 crontab 中文问题
CRONTAB_COMMAND_PREFIX = 'LANG_ALL=zh_cn.UTF-8'
"""
添加定时任务到系统中
python manage.py crontab add

显示已激活的定时任务
python manage.py crontab show

移除定时任务
python manage.py crontab remove
"""

# 配置数据库读写路由
DATABASE_ROUTERS = ['Django_Project.utils.db_router.MasterSlaveDBRouter']

# 表示允许所有的域名跨域访问本服务器
# CORS_ORIGIN_ALLOW_ALL = True

# CORS 添加白名单，凡是出现在白名单中的域名，都可以跨域访问本服务器
CORS_ORIGIN_WHITELIST = [
    'http://127.0.0.1:8080',
    'http://localhost:8080',
    'http://www.meiduo.site:8080',
    'http://api.meiduo.site:8000'
]

# 可设置允许跨域访问本服务器的请求方法
# CORS_ALLOW_METHODS = []

CORS_ALLOW_CREDENTIALS = True  # 指明在跨域访问中，后端支持对cookie的操作

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 添加JWT认证方式
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

# JWT配置
JWT_AUTH = {
    # JWT_EXPIRATION_DELTA 指明token的有效期
    # datetime.timedelta(days=1)构建一个时间段对象
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
    # 指明jwt认证成功返回数据的函数
    # 'JWT_RESPONSE_PAYLOAD_HANDLER': 'Django_Project.utils.jwt_response.jwt_response_payload_handler',
}

# 配置djcelery任务
djcelery.setup_loader()
BROKER_URL = 'redis://:myredis@127.0.0.1:6379/8'
CELERY_RESULT_BACKEND = 'redis://:myredis@127.0.0.1:6379/8'
# 设定导入任务
CELERY_IMPORTS = ('Django_Project.apps.project_admin.tasks', )
