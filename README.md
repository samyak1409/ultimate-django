# Django E-Commerce (RESTful API)

✅ Built the backend for a full-featured e-commerce application using Django & Django REST framework.

✅ Designed RESTful APIs supporting CRUD operations, search, sorting, pagination, and secure authentication/authorization using JSON Web Tokens (JWT).

✅ Optimized application performance by implementing Redis caching, executing background jobs with Celery, and writing automated tests with pytest to ensure code quality, scalability, and industry best practices.

## Setup

1. Clone the repository

   ```sh
   git clone https://github.com/samyak1409/ultimate-django.git
   cd ultimate-django
   ```

2. Create and activate virtual environment

   ```sh
   pip install pipenv
   pipenv shell
   ```

3. Install dependencies

   ```sh
   pipenv install --dev
   ```

4. Create the PostgreSQL database

   The dev settings ([storefront/settings/dev.py](storefront/settings/dev.py)) expect a local PostgreSQL server with a database named `ultimate_django` — adjust the credentials there to match your setup, then:

   ```sh
   createdb ultimate_django
   ```

5. Apply migrations

   ```sh
   python manage.py migrate
   ```

6. (Optional) Seed the database with sample collections & products

   ```sh
   python manage.py seed_db
   ```

7. Run the development server

   ```sh
   python manage.py runserver
   ```

   Server will start at: [127.0.0.1:8000](http://127.0.0.1:8000)

## Background Tasks (optional)

Celery and the cache both use a local Redis server (`127.0.0.1:6379`). With Redis running:

```sh
celery -A storefront worker --loglevel=info   # worker
celery -A storefront beat                     # periodic task scheduler
celery -A storefront flower                   # monitoring dashboard (localhost:5555)
```

(The API itself works fine without Redis — cache errors are treated as cache misses.)

## Running Tests

```sh
pytest
```
