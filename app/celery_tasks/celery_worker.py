from celery import Celery
from app.core.config import CeleryConfig

celery_app = Celery("celery_app")
celery_app.conf.update(broker_url=CeleryConfig.BROKER_URL,
                       result_backend=CeleryConfig.RESULT_BACKEND,
                       broker_connection_retry_on_startup=True)

celery_app.autodiscover_tasks(['app.celery_tasks'])

