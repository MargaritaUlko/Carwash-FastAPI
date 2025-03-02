from celery import Celery
from celery.schedules import crontab
import logging

# Инициализация Celery с брокером памяти
celery_app = Celery('tasks', broker='memory://')  # Брокер памяти
# celery_app.autodiscover_tasks(['smtp.tasks'])
celery_app.autodiscover_tasks(['core.email_sending.tasks, core'])
celery_app.conf.broker_connection_retry_on_startup = True

# Автозагрузка задач из модулей


# Настройки Celery
celery_app.conf.update(
    task_serializer='json',
    timezone='UTC',
    worker_pool='prefork',
    loglevel='DEBUG',
)

# Планировщик задач
celery_app.conf.beat_schedule = {
    "notify-expired-orders": {
        "task": "tasks.notify_users_about_expired_orders",
        "schedule": crontab(minute="*/5"),
    },
    "update-expired-orders-status": {
        "task": "tasks.update_expired_orders_status",
        "schedule": crontab(minute="*/1"),
    },

}

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


