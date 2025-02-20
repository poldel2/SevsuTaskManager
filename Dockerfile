# backend/Dockerfile
FROM python:3.11


COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Запуск миграций перед запуском приложения
CMD alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000