FROM python:3.12-slim

# Настройка окружения: запрещаем Python писать файлы .pyc и включаем буферизацию логов
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /code

# Сначала копируем только зависимости (для кэширования слоев Docker)
COPY ./requirements.txt /code/requirements.txt

# Обновляем pip и устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --upgrade -r ./requirements.txt

# Копируем всю папку с кодом приложения в контейнер
COPY ./src /code/app

# Запуск приложения (хост 0.0.0.0 обязателен для Docker)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]