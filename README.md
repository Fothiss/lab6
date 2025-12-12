# Лабораторная работа 6 - REST API для управления пользователями

## Технологии
- Python 3.12.8
- Litestar
- SQLAlchemy + SQLite
- Pydantic
- Docker
- UV (менеджер зависимостей)
- Linters: pre-commit, black, isort, pylint
- RabbitMQ


## Установка и запуск через Docker

### 1. Клонируйте репозиторий
```bash
git clone <url-репозитория>
cd lab6
```

### 2. Соберите и запустите контейнер
```bash
docker-compose up --build
```
### 3. Проверка работы RabbitMQ
```bash
docker-compose exec app uv run python -m app.messaging.seed_rabbit
```

## Команды для командной строки
### Вывод пользователей
```bash
curl "http://localhost:8000/users"
```

### Добавление пользователя
```bash
curl -X POST "http://localhost:8000/users" -H "Content-Type: application/json" -d "{\"username\":\"newuser\",\"email\":\"newuser@university.ru\"}"
```

### Вывод пользователя по ID
```bash
curl "http://localhost:8000/users/3"
```

### Изменение информации о пользователе
```bash
curl -X PUT "http://localhost:8000/users/3" -H "Content-Type: application/json" -d "{\"email\":\"updated@university.ru\"}"
```

### Удаление информации о пользователе
```bash
curl -X DELETE "http://localhost:8000/users/3"
```

### Получение информации по фильтру
```bash
curl "http://localhost:8000/users?username=kozlov"
```

## Тестирование

### 1. Запуск всех тестов
```bash
pytest
```
### 2. Запуск unit-тестов
#### Репозитории
```bash
pytest tests/test_repositories
```

#### Сервисы
```bash
pytest tests/test_services
```

#### API-ендпоинты
```bash
pytest tests/test_controllers
```

### 3. Отчет о покрытии
```bash
pytest --cov-report=html
```