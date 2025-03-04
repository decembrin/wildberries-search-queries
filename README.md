# Wildberries Search Queries

## Описание
Этот cервис предназначен для обработки и анализа поисковых запросов Wildberries. Он включает в себя несколько сервисов, таких как FastAPI для обработки HTTP-запросов, Celery для выполнения фоновых задач и PostgreSQL для хранения данных. Redis используется для кэширования, а RabbitMQ как бэкенд для Celery.

## Структура проекта
- `src/` - исходный код проекта
  - `application/` - бизнес-логика и use cases
  - `domain/` - доменные сущности и интерфейсы
  - `infrastructure/` - инфраструктурные компоненты, такие как репозитории и кэши
  - `presenters/` - слой представления, включая HTTP-сервер и маршруты
- `docker/` - файлы для Docker-контейнеров
- `docker-compose.yml` - конфигурация Docker Compose
- `requirements.txt` - зависимости проекта

## Запуск
1. Клонируйте репозиторий:
```sh
git clone https://github.com/your-repo/wildberries-search-queries.git
cd wildberries-search-queries
```

2. Создайте файл с переменными окружения. Пример файла .env:

```txt
DEBUG=true
TIME_ZONE=Europe/Moscow
USE_TZ=true
APP_PORT=8000
APP_HOST=0.0.0.0

POSTGRES_DRIVER=postgresql+asyncpg
POSTGRES_HOST=postgresql
POSTGRES_USER=service
POSTGRES_DB=service
POSTGRES_PASSWORD=password

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

BROKER_HOST=rabbitmq
BROKER_USERNAME=user
BROKER_PASSWORD=password
BROKER_DB=search-queries-service

WB_AUTHORIZEV3=
WB_WBX_VALIDATION_KEY=
```

4. Запустите Docker Compose:
```sh
docker compose up -d
```

5. Выполнить миграции:
```sh
docker exec -it App alembic upgrade head
```

## Использование
После запуска Docker Compose, приложение будет доступно по адресу `http://localhost:8000`.

## #TODO
1. Починить загрузку поисковых запросов из файла
2. Добавить unit и integration тесты
3. Добавить документацию к коду
4. Доработать документацию к API
5. Сделать настройку CORS через config