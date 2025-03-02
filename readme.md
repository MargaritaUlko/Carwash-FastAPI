Carwash FasyAPU — API для управления заказами и услугами
Этот проект представляет собой API для системы, которая управляет заказами и услугами в сервисе по обслуживанию автомобилей. В нем реализованы CRUD операции для различных сущностей, фильтрация, сортировка и пагинация данных.

**Запуск проекта**
Важно сразу заполнить поля FROM_EMAIL, TO_EMAIL, SMTP_PASSWORD в env.py, эти характеристки отвечают за отправку сообщений на почту через SMTP клиент.  
По команде docker-compose up --build

*Структура Базы Данных*
Для построения базы данных был использован следующий дизайн:
Схема базы данных - https://drawsql.app/teams/alexxx/diagrams/servicev2

Система включает несколько сущностей:

Cars: Машины клиентов, включая информацию о марке и модели.
Services: Услуги, такие как мойка окон, с ценой и временем выполнения.
Users: Пользователи, с ролями (администратор, работник, клиент).
CustomerCars: Связь между машинами клиентов и пользователями.
Orders: Заказы, содержащие информацию о выбранных услугах, машине клиента и работниках.

**Основные Особенности API**
1. CRUD операции
Каждая сущность поддерживает стандартные операции:

Create: Создание новой записи.
Read: Получение информации.
Update: Обновление существующей записи.
Delete: Удаление записи.
2. Фильтрация
Каждую сущность можно фильтровать по различным полям. Пример фильтрации:

Для услуги можно фильтровать по цене.
Для машины — по марке и модели.
Для заказов — по статусу или дате.
3. Сортировка
Данные могут быть отсортированы по выбранным полям. Например:

Услуги могут быть отсортированы по цене или времени.
Заказы могут быть отсортированы по дате создания или статусу.
4. Пагинация
Для всех сущностей поддерживается пагинация, что позволяет ограничить количество возвращаемых данных за один запрос.

Проверка ролей
В системе три роли пользователей:

Администратор: Может создавать, обновлять и удалять все сущности.
Работник: Может просматривать свои заказы и обновлять их статус.
Клиент: Может просматривать свои заказы и обновлять их статус.
Только администратор может создавать заказы и редактировать все сущности. Работники и клиенты могут взаимодействовать только с заказами, которые им принадлежат.

Если у клиента поле is_send_notify установлено в true, то после завершения заказа будет отправлено уведомление на email.

Логика заказа
При создании заказа:

Указываются выбранные услуги.
Для каждой услуги рассчитывается время выполнения и стоимость.
Время выполнения и стоимость суммируются для всего заказа.
В ответе на создание заказа будут возвращены все данные, включая общую стоимость и время.

**Примечание**
Если в заказ уже добавлена услуга, попытка добавить её снова вызовет ошибку.
Сервисный слой
Логика обработки данных и взаимодействия с базой данных вынесена в сервисный слой, который обрабатывает все бизнес-операции. Контроллеры (или API-методы) только получают запросы и передают их сервисному слою.

**Технологии**
FastAPI: для создания API
PostgreSQL: для хранения данных
SQLAlchemy: для работы с базой данных
Celery: для отправки уведомлений на email
Docker: для контейнеризации приложения
