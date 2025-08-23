![Python](https://img.shields.io/badge/Python-3.12-green?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-green?logo=FastAPI)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-pink?logo=SQLAlchemy)
![PostgreSQL](https://img.shields.io/badge/Postgres-16-darkblue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-blue?logo=docker)
![Docker-Compose](https://img.shields.io/badge/DockerCompose-blue?logo=docker)

---

FastAPI Auth Service - это высокопроизводительный микросервис аутентификации, построенный на современном асинхронном фреймворке FastAPI. Сервис предоставляет полный цикл управления пользователями и безопасной аутентификации.

---

#### Endpoints
  
  Аутентификация
    - Регистрация нового пользователя
    - POST /auth/register
  ```
  POST "http://localhost:8000/auth/register" \
    -H "Content-Type: application/json" \
    -d '{
      "email": "user@example.com",
      "username": "user123",
      "password": "securepassword123"
    }'
  ```
  Response:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```
  Авторизация
    - Вход в систему
    - POST /auth/login
  ```
  curl -X POST "http://localhost:8000/auth/login" \
    -H "Content-Type: application/json" \
    -d '{
      "email": "user@example.com",
      "password": "securepassword123"
    }'
  ```
  Response:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```
  
  Управление пользователями
    - Получение информации о текущем пользователе
    - GET /auth/me
  ```
  curl -X GET "http://localhost:8000/auth/me" \
    params {"Token": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
  ```
  Response:
  ``` json
  {
    "id": 1,
    "email": "user@example.com",
    "username": "user123",
    "is_active": true,
    "created": "2025-08-23T17:53:00"
  }
  ```
---
#### Установка

1. **Клонируйте репозиторий:**

```bash
git clone https://github.com/wpotoke/authorization_service.git
cd auth_service
````

2. **Активируйте виртуальное окружени и установите зависисмости:**
```
python -m venv venv
pip install -r requirements.txt
```

4. **Создайте файл переменных окружения:**
.env
```
SECRET_KEY = "random secret key"

# database
DB_URL = "postgresql+asyncpg://{username}:{password}@db:5432/{db_name}"
SQL_USER=username
SQL_PASSWORD=db_password
SQL_DATABASE=db_name
```

5. **Сгенерируйте SECRET_KEY (если необходимо) и вставьте его в файл .env:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

5. **Создайте пользователя и базу данных, также передайте права на пользование и укажите кодировку**

```pqsl
CREATE USER your_username WITH PASSWORD 'your_password';
CREATE DATABASE your_databasename OWNER your_username ENCODING 'UTF8' LC_COLLATE 'ru_RU.UTF8' LC_CTYPE 'ru_RU.UTF8' TEMPLATE=template0;
```


6. **Соберите и запустите контейнеры:**

```bash
docker-compose up --build
```

Приложение будет доступно по адресу: [http://localhost:8000](http://localhost:8000)
