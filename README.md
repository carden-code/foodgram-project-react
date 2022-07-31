# Сайт Foodgram, «Продуктовый помощник»
 Проект Foodgram позволяет пользователем публиковать свои рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Стек технологий

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)

## Как запустить проект, используя Docker (база данных PostgreSQl):
Клонировать репозиторий и перейти в него в командной строке:
```bash
    git clone git@github.com:carden-code/foodgram-project-react.git
    cd foodgram-project-react
```
Создайте и активируйте виртуальное окружение:

```bash
python -m venv venv
source venv/Scripts/activate
```
В дериктории проекта создайте файл .env, в котором пропишите следующие переменные окружения (SECRET_KEY нужно взять из settings.py):
```python
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
DEBUGE=True
SECRET_KEY=<SECRET_KEY>
```

Соберите контейнеры:

```bash
    docker-compose up -d --build 
```
Выполните по очереди команды:

```bash
    docker-compose exec backend python manage.py makemigrations
    docker-compose exec backend python manage.py migrate
    docker-compose exec backend python manage.py add_ingredients
    docker-compose exec backend python manage.py createsuperuser
    docker-compose exec backend python manage.py collectstatic --no-input 
```
____
Ваш проект запустился на http://localhost/
