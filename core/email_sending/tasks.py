
import logging
from datetime import datetime

import pytz
from sqlalchemy import select
from celery import chain

import asyncio
from sqlalchemy.orm import aliased
from .celery_app import celery_app

from core.email_sending.send_email import send_email
from ..models import Order, User, db_helper, Customer_Car

# tasks.py
# celery_app.config_from_object('celery_app')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Задачи Celery



@celery_app.task
def update_expired_orders_status():
    asyncio.run(update_expired_orders_status_async())


async def update_expired_orders_status_async():
    async for session in db_helper.session_getter():
        krasnoyarsk_tz = pytz.timezone("Asia/Krasnoyarsk")
        now = datetime.now(krasnoyarsk_tz)

        result = await session.execute(select(Order))
        expired_orders = result.scalars().all()

        logger.debug(f"Дата и время: {now}, Часовой пояс: {krasnoyarsk_tz}")


        # logger.debug(f"Found {len(expired_orders)} expired orders.")

        for order in expired_orders:
            if not order.notified:
                order.status = 0
                session.add(order)
                logger.debug(f"Статус заказ {order.id} обновлен на 0.")

        await session.commit()

        # krasnoyarsk_tz = pytz.timezone("Asia/Krasnoyarsk")
        # now = datetime.now(krasnoyarsk_tz)


        result = await session.execute(
            select(Order).filter(Order.status == 0, Order.notified == False)
        )
        expired_orders = result.scalars().all()
        logger.debug(f"Найдено {len(expired_orders)} истекших заказов.")


        for order in expired_orders:
            customer_car = await session.execute(
                select(Customer_Car).filter(Customer_Car.id == order.customer_car_id)
            )
            customer_car = customer_car.scalar_one_or_none()

            if customer_car:

                user = await session.execute(
                    select(User).filter(User.id == customer_car.customer_id)
                )
                user = user.scalar_one_or_none()

                if user:
                    logger.debug(f"Пишем юзеру {user.email} о заказе {order.id}")

                    subject = "Ваш заказ бал выполнен"
                    body = f"Уважаемый {user.first_name},\n\n Ваш заказ под номером {order.id} выполнен. Как все прошло?.\n\n До встречи,\n SLAY Entartainment"

                    send_email(user.email, subject, body)

                    order.notified = True
                    await session.commit()
                else:
                    logger.debug(f"Нет пользователя для машины {customer_car.id}")
            else:
                logger.debug(f"Нет машины для заказа {order.id}")


