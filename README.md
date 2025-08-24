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

| REGISTER | LOGIN | ME |
|----------|-------|----|
| <img width="1379" height="703" alt="изображение" src="https://github.com/user-attachments/assets/b8513667-7b2b-400f-b2e0-e27e7cffdc2d" /> | <img width="1385" height="703" alt="изображение" src="https://github.com/user-attachments/assets/a63c3524-3299-4d69-9cfb-31f551a37556" /> | <img width="1388" height="737" alt="изображение" src="https://github.com/user-attachments/assets/d14fced5-0460-464b-b466-823c796a118e" /> |


| REFRESH | LOGOUT |
|---------|--------|
| <img width="1376" height="751" alt="Снимок экрана 2025-08-24 004353" src="https://github.com/user-attachments/assets/0b1e813c-5a1b-497a-86dd-1528362780ad" /> | <img width="1383" height="659" alt="Снимок экрана 2025-08-24 004412" src="https://github.com/user-attachments/assets/568815e1-20c8-4667-b65f-4afb5fd4d301" /> | 
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

#### Тестирование

```bash
docker-compose exec web pytest tests/
```
после данных действий приложение будет доступно 
- Health ([дает понять что приложение работает](https://127.0.0.1:8000/))
- Документация: [http://localhost:8000/docs#](https://127.0.0.1:8000/docs#)
