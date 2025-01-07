
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # 'config.settings' to'g'ri ekanini tasdiqlang
application = get_wsgi_application()

