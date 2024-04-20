from celery import Celery


celery_app = Celery("celery_app")
celery_app.config_from_object("app.celery_tasks.config")

