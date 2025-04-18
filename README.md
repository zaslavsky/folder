# Проект Estate4Rent

## Описание
Estate4Rent — это API для управления арендой недвижимости. С помощью этого API пользователи могут:
- Регистрироваться и авторизовываться.
- Создавать, просматривать, обновлять и удалять объекты недвижимости.
- Бронировать объекты недвижимости.
- Оставлять отзывы.
- Просматривать историю поиска.

## Установка и запуск

### Требования
- Python 3.10+
- Poetry

### Запуск с использованием Docker Compose
1. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/zaslavsky/folder
   cd folder
   ```
2. Постройте и запустите контейнеры:
   ```bash
   docker-compose up --build
   ```
3. API будет доступен по адресу: `http://localhost:8000`

### Локальный запуск
1. Установите зависимости с помощью Poetry:
   ```bash
   poetry install
   ```
2. Примените миграции:
   ```bash
   poetry run python manage.py migrate
   ```
3. Запустите сервер разработки:
   ```bash
   poetry run python manage.py runserver
   ```
4. API будет доступен по адресу: `http://localhost:8000`

## Документация API
Документация доступна по следующим адресам:
- Swagger UI: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- ReDoc: [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)

## Переменные окружения
- `PYTHONDONTWRITEBYTECODE=1` — отключает создание файлов `.pyc`.
- `PYTHONUNBUFFERED=1` — отключает буферизацию вывода Python.

## Структура проекта
- `api/` — приложение с основной логикой API.
- `rental_app/` — настройки проекта Django.
- `Dockerfile` — конфигурация для сборки Docker-образа.
- `docker-compose.yml` — конфигурация для запуска контейнеров.

