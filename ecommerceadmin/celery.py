from celery import Celery
from django.conf import settings
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerceadmin.settings')

app = Celery('ecommerceadmin')

# Configuración general de Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descubrir tareas automáticamente en las aplicaciones
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
