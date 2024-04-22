from celery import Celery


celery_app = Celery("celery_app")
celery_app.conf.update(broker_url="amqp://guest:guest@rabbitmq:5672",
                       result_backend="rpc://",
                       broker_connection_retry_on_startup=True)

