# Image Processor

API-клиент для быстрой обработки изображений к различным размерам: thumb, big_thumb, big_1920, d2500 и мнгновенной выгрузки в S3.

## Стэк:
  * Python: 3.11
  * Web: FastAPI
  * СУБД: PostgreSQL
  * Обработка изображений: Pillow
  * Фоновая обработка задач: Celery(broker: RabbitMQ, backend: Redis)
  * S3-хранилище: Minio
  * Контейнирезация: Docker

## Установка и запуск
<details>
### Для разработки:

* После клонирования репозитория находять в директории с приложением установите виртуальное окружение и примените зависимости из файла `requirements.txt`:

```sh
python3.11 -m venv venv

pip install -r requirements.txt
```

* Подготовьте файл `.env` с переменными окржения:
```
# POSTGRES
APP_CONF__DB__URL=postgresql+asyncpg://user:password@localhost:5432/db_name
# MINIO
APP_CONF__MINIO__ENDPOINT=http://127.0.0.1:9000
APP_CONF__MINIO__ACCESS_KEY=<your_access_key>
APP_CONF__MINIO__SECRET_KEY=<your_secret_key>
# SESSION MIDDLEWARE
APP_CONF__SECRET_KEY=YOURSECRETKEY
# CELERY
APP_CONF__CELERY__BROKER=amqp://rmuser:rmpassword@localhost:5672//
APP_CONF__CELERY__BACKEND=redis://localhost:6379/0
#INIT POSGRESQL:
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=db_name
# INIT MINIO:
MINIO_ROOT_USER=yuor_minio_user
MINIO_ROOT_PASSWORD=yuor_minio_password
# INIT RABBITMQ:
RABBITMQ_DEFAULT_USER=rmuser
RABBITMQ_DEFAULT_PASS=rmpassword
RABBITMQ_SERVER_ADDITIONAL_ERL_ARGS=-rabbit disk_free_limit 2147483648
```

Обратите Ваше внимание, что после запуска контейнеров с PostgreSQL, Minio и тд, необходимо перейти по адресу http://127.0.0.1:9001 используя выши MINIO_ROOT_USER и MINIO_ROOT_PASSWORD чтобы получить ACCESS_KEY и SECRET_KEY в разделе `Keys` для работы приложения с Minio.
</details>
