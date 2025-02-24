# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем необходимые зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libsqlite3-dev \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libatlas-base-dev \
    libgtk-3-dev \
    python3-dev \
    python3-pip

# Создаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей и устанавливаем их
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . /app/

# Запускаем миграции и собираем статику
RUN python manage.py makemigrations
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

# Устанавливаем gunicorn
RUN pip install gunicorn

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["gunicorn", "RobotStuartRzd.wsgi:application", "--bind", "0.0.0.0:8000"]
