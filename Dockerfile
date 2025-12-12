FROM python:3.12-slim

WORKDIR /app

# Устанавливаем UV
RUN pip install uv

# Копируем зависимости
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости
RUN uv sync --frozen

# Копируем код приложения
COPY . .

ENV PYTHONPATH="/app"

# Запускаем приложение
CMD ["sh", "-c", \
    "echo '=== Запуск лабораторной работы ===' && \
     uv run python scripts/load_data.py && \
     uv run python scripts/update_data.py && \
     uv run python -m app.main"]