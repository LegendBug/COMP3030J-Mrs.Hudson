import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-(5a5(g(-94lpvgwef13(iza+5^=#we4ts*9c^0g9*@km@&2p50'

# ALLOWED_HOSTS = []
ALLOWED_HOSTS = ["*"]  # TODO 在测试时使用，允许所有的主机访问;在部署上线前,应该更改为允许访问的主机的IP地址和域名(即我的云服务器的ip地址和我购买的域名)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'crispy_forms',
    "crispy_bootstrap5",
    "django_extensions",
    'gunicorn',
    'Inventory',
    'User',
    'Statistic',
    'Layout',
    'System',
    'Venue',
    'Exhibition',
    'Booth',
]

# 配置Django crispy_forms包的表单渲染模板
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # 添加corsheaders中间件以处理跨域请求
    'COMP3030J_Hudson.middleware.LoginRequiredMiddleware',  # 添加自定义中间件以处理登录验证
]

ROOT_URLCONF = 'COMP3030J_Hudson.urls'

TEMPLATES = [
    # Django模板引擎
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # 可以添加templates文件夹的路径: os.path.join(BASE_DIR, 'templates')
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'COMP3030J_Hudson.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# 不使用Docker来管理项目的各个容器时,请使用以下配置:
load_dotenv()
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('MYSQL_DATABASE', 'hudson'),
        'USER': os.getenv('DB_USERNAME', 'root'),
        'PASSWORD': os.getenv('MYSQL_ROOT_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

# Internationalization 国际化
# https://docs.djangoproject.com/en/5.0/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Shanghai' # TODO 部署的时候要改成 TIME_ZONE = 'Europe/Dublin'
USE_I18N = True
USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 配置Django日志
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {  # 只针对请求日志
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# 配置django_extensions的models可视化插件
GRAPH_MODELS = {  # python manage.py graph_models -a -o ER_Diagram.png
    'all_applications': True,
    'group_models': True,
    'app_labels': ["Inventory", "User", 'Statistic', 'Layout', 'System', 'Venue', 'Exhibition',
                   'Booth', "auth"],
}

# 配置CORS:
CORS_ALLOW_ALL_ORIGINS = True

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  # 为True时, 404拦截器将不会生效, 这样便于debug
#DEBUG = False  # 当 DEBUG 设置为 True 时，Django 会自动服务静态文件，但在生产环境中，你应该通过 Web 服务器来处理静态文件的服务。确保在生产环境将 DEBUG 设置为 False 并正确配置静态文件服务

# --------------------------------------------------------- Media Settings ---------------------------------------------------------
# 配置ImageField的上传路径
MEDIA_ROOT = os.path.join(BASE_DIR, 'static/data')  # 配置 MEDIA_ROOT 至项目根目录下的 'static/data' 文件夹
MEDIA_URL = '/data/'  # 配置 MEDIA_URL，用于访问媒体资源

# --------------------------------------------------------- Static Settings ---------------------------------------------------------
# Static files (CSS, JavaScript, Images) 静态文件, 详见https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = 'static/'
STATICFILES_DIRS = [  # 静态文件目录,用于指定非static文件夹下的静态文件的位置
    BASE_DIR / 'static',
]

# STATIC_ROOT 是收集完成后静态文件的目的地，即所有使用 collectstatic 命令从 STATICFILES_DIRS 和你的应用中的 static 文件夹中复制来的文件都会被存储到这个目录。在生产环境中，你的 web 服务器（如 Nginx 或 Apache）将从这个目录提供静态文件。
STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
