FROM python:3.10-slim

# Установим системные зависимости
# - ffmpeg: для обработки аудио/видео (используется yt-dlp)
# - tini: простой init-процесс для правильной обработки сигналов и зомби-процессов в контейнере (рекомендуется для Gunicorn)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    tini \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями и устанавливаем их
COPY requirements.txt .
# Обновляем pip и устанавливаем Gunicorn отдельно для лучшего кэширования слоев
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir gunicorn
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код приложения
COPY . .

# Указываем порт, который будет слушать контейнер (Gunicorn будет использовать переменную $PORT)
# Render автоматически устанавливает переменную PORT.
# Эта инструкция EXPOSE больше для документации и для локального запуска Docker.
EXPOSE 8080

# Используем tini в качестве точки входа для корректного управления процессами
ENTRYPOINT ["/usr/bin/tini", "--"]

# Команда для запуска приложения через Gunicorn
# Gunicorn будет слушать порт, указанный в переменной окружения PORT
# app:app означает: файл app.py, переменная app (в которой Flask(__name__))
# Настройки workers, threads, timeout можно будет подобрать позже.
CMD ["sh", "-c", "echo The port is $PORT && gunicorn --bind 0.0.0.0:$PORT --workers 1 app:app"]
