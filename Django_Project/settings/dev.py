"""
Django settings for Django_Project project.

Generated by 'django-admin startproject' using Django 1.11.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os, sys

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

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'users',
]

MIDDLEWARE = [
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
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 数据库引擎
        'HOST': '127.0.0.1',  # 数据库主机
        'PORT': 3306,  # 数据库端口
        'USER': 'yin',  # 数据库用户名
        'PASSWORD': 'mysql',  # 数据库用户密码
        'NAME': 'django_project'  # 数据库名字
    },
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

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

# 存放查找静态文件的目录 接收的是list
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

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
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": "myredis",  # requirepass:myredis
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
            "DECODE_RESPONSES": True
        }
    },
    "session": {
        # 后端RedisCache
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": "myredis",  # requirepass:myredis
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
            "DECODE_RESPONSES": True
        }
    }
}

# 设置将session存储到redis中
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"

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

# 指定本项目的用户模型类
AUTH_USER_MODEL = 'users.User'
