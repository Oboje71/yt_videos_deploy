# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# (Опционально) Если нужны системные зависимости, например, ffmpeg для обработки видео
# RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Копируем остальной код приложения в рабочую директорию
COPY . .

# Указываем порт, на котором будет работать приложение (Render обычно предоставляет его через переменную PORT)
ENV PORT 8080
EXPOSE 8080

# Команда для запуска приложения (Render обычно использует Procfile, но это может быть здесь как CMD)
# CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT"]
# Если используешь Procfile, то CMD здесь может быть не так важен или может быть другим.
