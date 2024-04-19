from celery import Celery


celery_app = Celery("celery_app")
celery_app.conf.broker_connection_retry_on_startup = True
celery_app.conf.broker_url = "amqp://guest:guest@localhost:5672"
celery_app.conf.result_backend = "rpc://"

