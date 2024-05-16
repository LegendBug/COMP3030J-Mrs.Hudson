import os
from django.core.wsgi import get_wsgi_application
from django.contrib.staticfiles.handlers import StaticFilesHandler  # 添加模块

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'COMP3030J_Hudson.settings')

application = get_wsgi_application()
# application = StaticFilesHandler(get_wsgi_application())
