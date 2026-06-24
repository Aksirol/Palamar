# Використовуємо офіційний легкий образ Python 3.12
FROM python:3.12-slim

# Встановлюємо змінні середовища
# PYTHONDONTWRITEBYTECODE - щоб Python не створював файли .pyc
# PYTHONUNBUFFERED - щоб логи одразу виводилися в термінал
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

# Встановлюємо системні залежності, необхідні для WeasyPrint (PDF генерація)
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libjpeg-dev \
    libopenjp2-7-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Копіюємо файл із залежностями та встановлюємо їх
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Копіюємо весь проєкт у контейнер
COPY . /app/

# Скрипт запуску — робимо виконуваним
RUN chmod +x /app/start_render.sh

# Відкриваємо порт
EXPOSE 8000

# Локальна розробка — перевизначається у docker-compose.yml
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]