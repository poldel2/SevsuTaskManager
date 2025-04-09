# backend/Dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Создаем директорию для логов и настраиваем права
RUN mkdir -p /app/logs && chmod 777 /app/logs

COPY . .

# Запуск миграций перед запуском приложения
CMD alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000