
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



#
#
# @celery_app.task
# def notify_users_about_expired_orders(*args, **kwargs):
#     try:
#         loop = asyncio.new_event_loop()  # Создаем новый цикл событий
#         asyncio.set_event_loop(loop)  # Устанавливаем этот цикл как текущий
#         loop.create_task(notify_users_about_expired_orders_async())
#     except Exception as e:
#         logger.error(f"Error in notify_users_about_expired_orders: {e}")
# async def notify_users_about_expired_orders_async():
#     # Использование асинхронного контекстного менеджера
#
#     async for session in db_helper.session_getter():
#         logger.debug("Starting notify_users_about_expired_orders_async")
#         # krasnoyarsk_tz = pytz.timezone("Asia/Krasnoyarsk")
#         # now = datetime.now(krasnoyarsk_tz)
#
#         # Ищем истекшие заказы, которые ещё не были уведомлены
#         result = await session.execute(
#             select(Order).filter(Order.status == 0, Order.notified == False)
#         )
#         expired_orders = result.scalars().all()
#         logger.debug(f"Found {len(expired_orders)} expired orders for notification.")
#         logger.info(f"Found {len(expired_orders)} expired orders for notification.")
#         # Для каждого истекшего заказа ищем клиента
#         for order in expired_orders:
#             # Ищем машину клиента
#             customer_car = await session.execute(
#                 select(Customer_Car).filter(Customer_Car.id == order.customer_car_id)
#             )
#             customer_car = customer_car.scalar_one_or_none()
#
#             if customer_car:
#                 # Ищем пользователя (клиента) по customer_id
#                 user = await session.execute(
#                     select(User).filter(User.id == customer_car.customer_id)
#                 )
#                 user = user.scalar_one_or_none()
#
#                 if user:
#                     logger.debug(f"Notifying user {user.email} about expired order {order.id}")
#
#                     # Формируем сообщение
#                     subject = "Your order has expired"
#                     body = f"Dear {user.first_name},\n\nYour order with ID {order.id} has expired. Please check your account for more details.\n\nBest regards,\nYour Company"
#
#                     # Отправляем уведомление
#                     send_email(user.email, subject, body)
#
#                     # Обновляем поле notified у заказа
#                     order.notified = True
#                     await session.commit()
#                 else:
#                     logger.debug(f"No user found for customer car ID {customer_car.id}")
#             else:
#                 logger.debug(f"No customer car found for order ID {order.id}")
#





chain(
    update_expired_orders_status.s(),

)()









# @celery_app.task
# def simple_task():
#     logger.debug("This is a simple task!")
#
# # Задача для уведомлений об истекших заказах
# @celery_app.task
# def notify_users_about_expired_orders():
#     logger.debug("Notifying users about expired orders.")
#
# # Задача для обновления статуса заказов
# @celery_app.task
# def update_expired_orders_status():
#     logger.debug("Updating status of expired orders.")
#
# simple_task.delay()
# notify_users_about_expired_orders.delay()
# update_expired_orders_status.delay()
