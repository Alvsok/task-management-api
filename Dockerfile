# Используем официальный образ Python 3.12
FROM python:3.12-slim

# Метаданные
LABEL maintainer="alvsok@github.com"
LABEL description="Task Management API - Django REST Framework"

# Переменные окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Рабочая директория
WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    gcc \
    python3-dev \
    libpq-dev \
    netcat-traditional \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копирование и установка Python зависимостей
COPY requirements.txt /app/
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Копирование кода проекта
COPY . /app/

# Создание непривилегированного пользователя
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Переключение на непривилегированного пользователя
USER appuser

# Открытие порта
EXPOSE 8000

# CMD будет переопределена в docker-compose.yml
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
