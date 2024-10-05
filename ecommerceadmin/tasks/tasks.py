from celery import shared_task
from django.core.cache import cache

@shared_task
def limpiar_cache():
    cache.clear()  # Limpia la caché