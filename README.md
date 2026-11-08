## Быстрый запуск с существующей базой

1. Распакуйте проект в новую папку. Сохраните свою папку pgsql и существующую базу hr_ipr.
2. Откройте PowerShell в папке проекта. Создайте отдельное окружение и установите зависимости:

~~~powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
~~~

Активация окружения не требуется. Устанавливаются только библиотеки внутри папки проекта.

3. Проверьте .env. Для присланной конфигурации:

~~~dotenv
DATABASE_URL=postgresql://postgres@localhost:5432/hr_ipr
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
~~~

4. Запустите переносную PostgreSQL.

Откройте PowerShell в папке проекта. Если папка `pgsql` находится рядом с папкой проекта, выполните:

~~~powershell
$projectPgRoot = '..\pgsql'
~~~

Если PostgreSQL расположена в другом месте, укажите путь к папке, содержащей `bin` и `data`:

~~~powershell
$projectPgRoot = 'C:\путь\к\pgsql'
~~~

Затем запустите сервер базы данных:

~~~powershell
& "$projectPgRoot\bin\pg_ctl.exe" -D "$projectPgRoot\data" -l "$projectPgRoot\logfile.txt" -o "-h 127.0.0.1 -p 5433" -w start
~~~

Если PostgreSQL уже запущена на этом порту, повторный запуск не требуется. В файле `.env` порт в `DATABASE_URL` также должен быть `5433`.

5. Запустите API из папки проекта:

~~~powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
~~~

Оставьте терминал открытым и перейдите в браузере по адресу http://localhost:8000/docs.

Для остановки API нажмите **Ctrl+C**.
~~~

Если база уже запущена, достаточно второй команды. Открывайте http://localhost:8000/docs.

## Как входить в Swagger

Нажмите Authorize вверху страницы. В username укажите полный email, в password - password123. Поля client_id и client_secret оставьте пустыми. Нажмите Authorize, затем Close.

Проверьте GET /auth/me и GET /development-plans/. Старая авторизация после замены кода может содержать неправильный токен: нажмите Logout и войдите заново.

Обычный Execute у POST /auth/login только возвращает токен. Для автоматической передачи токена остальным запросам используйте верхнюю кнопку Authorize.

| Роль | Email |
|---|---|
| Руководитель | ivanov@company.com |
| Сотрудник | petrova@company.com |
| Сотрудник | sidorov@company.com |
| Руководитель | kozlova@company.com |
| Руководитель | morozova@company.com |
| HR в новом наполнении | pavlova@company.com |

В старом дампе Павлова имеет роль manager. Для проверки HR без пересоздания своей базы сначала сохраните резервную копию и затем выполните scripts/set_demo_hr.sql:

~~~powershell
& 'C:\путь\к\pgsql\bin\pg_dump.exe' -U postgres -d hr_ipr -F p -f '.\hr_ipr_before_changes.sql'
& 'C:\путь\к\pgsql\bin\psql.exe' -U postgres -d hr_ipr -v ON_ERROR_STOP=1 -f '.\scripts\set_demo_hr.sql'
~~~

Успешный вход не даёт всем одинаковые права: сотрудник ведёт свои ИПР, руководитель просматривает и согласовывает ИПР прямых активных подчинённых, HR ведёт компетенции. Руководитель и HR также ведут собственные ИПР.

## Демонстрационная база для сдачи

В старом наполнении есть противоречия ТЗ. Готовый hr_ipr_demo.sql содержит согласованные данные, роль HR и ограничения БД. Восстанавливайте его в новую базу, сохраняя свою hr_ipr:

~~~powershell
& 'C:\путь\к\pgsql\bin\createdb.exe' -U postgres hr_ipr_demo
& 'C:\путь\к\pgsql\bin\psql.exe' -U postgres -d hr_ipr_demo -v ON_ERROR_STOP=1 -f '.\hr_ipr_demo.sql'
~~~

Затем замените только имя базы в .env:

~~~dotenv
DATABASE_URL=postgresql://postgres@localhost:5432/hr_ipr_demo
~~~

pg_dump создаёт дамп, а psql -f читает SQL-дамп и восстанавливает данные. Представленная в сообщении команда pg_dump не предназначена для чтения дампа.

Альтернатива для новой пустой базы: укажите её в .env и выполните:

~~~powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe scripts/seed_data.py
~~~

Повторный seed_data.py сохраняет существующую базу с пользователями. Опция --reset намеренно удаляет все данные модуля и создаёт новые; для существующей учебной базы она не нужна.

Старые SQL и DBML из практических работ 1–2 сохранены как исходные материалы. У их пользователей пароль IprDemo2026!, у присланного дампа и нового seed - password123. Проверка поддерживает оба формата хешей: PBKDF2 и bcrypt.

## Проверки

~~~powershell
.\.venv\Scripts\python.exe scripts/check_data.py
~~~

Этот скрипт выполняет только чтение. create_all и уже применённые миграции не добавляют новые CHECK-ограничения в старый дамп. Для полной схемы используйте новую демонстрационную базу или отдельно подготовленную миграцию существующих данных. Старый дамп автоматически не переписывается.

~~~powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
$env:TEST_DATABASE_URL='postgresql://postgres@localhost:5432/postgres'
.\.venv\Scripts\python.exe -m pytest tests -q
~~~

Тесты сами создают уникальную временную базу и удаляют только её после прогона. Без TEST_DATABASE_URL тесты пропускаются.

В Postman импортируйте postman/HR_IPR.postman_collection.json и запустите всю коллекцию по порядку. Переменная base_url по умолчанию http://localhost:8000. Используйте демонстрационную базу: коллекция оставляет один завершённый ИПР и используемую им компетенцию для просмотра.

Результаты фактического прогона и соответствие требованиям находятся в docs/Проверка_проекта.md. Детали ответов без токенов и паролей - docs/API_results.json. В Swagger после входа подтверждён ответ 200.

## Структура

app/models - семь ORM-моделей с ключами, связями, CHECK и индексами. app/schemas - входные и выходные Pydantic-схемы. app/routers - HTTP API. app/services/plans.py - права, сроки, переходы статусов и транзакции ИПР. alembic - миграции. scripts - наполнение и проверка данных. tests - проверки API на PostgreSQL.

Общая валидация Pydantic возвращает 422, нарушение бизнес-правила - 400, неверный вход - 401, отсутствие прав - 403, отсутствующая запись - 404, конфликт сохранения - 409. Успешное создание - 201, удаление без тела - 204.

Веб-интерфейс React в этот backend не входит. Swagger служит интерфейсом проверки API.