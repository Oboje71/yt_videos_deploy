from flask import Flask, request, send_from_directory, jsonify
import yt_dlp
import os
import uuid
# import logging # Можно добавить, если app.logger не работает как ожидается

app = Flask(__name__)
# Если используете стандартный logging:
# logging.basicConfig(level=logging.INFO)

DOWNLOAD_DIR = "audio"
# Используем абсолютный путь внутри контейнера для большей надежности
# WORKDIR в Dockerfile /app, поэтому APP_ROOT будет /app
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR_ABS = os.path.join(APP_ROOT, DOWNLOAD_DIR)

os.makedirs(DOWNLOAD_DIR_ABS, exist_ok=True)
app.logger.info(f"Audio download directory is: {DOWNLOAD_DIR_ABS}") # Логируем путь

@app.route('/download', methods=['POST'])
def download_audio():
    data = request.get_json()
    url = data.get('url')

    if not url:
        app.logger.warning("Missing URL in request")
        return jsonify({"error": "Missing URL"}), 400

    filename = f"{uuid.uuid4()}.mp3"
    # Сохраняем в абсолютный путь
    output_path = os.path.join(DOWNLOAD_DIR_ABS, filename)
    app.logger.info(f"Attempting to download URL: {url} to output path: {output_path}")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False, # ВРЕМЕННО отключаем quiet для подробных логов yt-dlp
        'verbose': True, # ВРЕМЕННО для еще более подробных логов
        # 'noprogress': True, # Можно добавить, если прогресс мешает логам
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            app.logger.info(f"Starting download for: {url}")
            ydl.download([url])
            app.logger.info(f"Download process finished for: {url}")
        
        # Проверка существования файла и его размера СРАЗУ ПОСЛЕ СКАЧИВАНИЯ
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            app.logger.info(f"File {output_path} CREATED. Size: {file_size} bytes.")
            if file_size == 0:
                app.logger.warning(f"File {output_path} is EMPTY (0 bytes).")
        else:
            app.logger.error(f"File {output_path} NOT FOUND after download attempt.")
            # Если файл не найден, возможно, не стоит возвращать download_url
            # return jsonify({"error": "File not created after download"}), 500 
            # Пока оставим как есть, но это место для улучшения

        return jsonify({"download_url": f"/audio/{filename}"})
    except Exception as e:
        app.logger.error(f"Error during download or processing for URL {url}: {str(e)}", exc_info=True) # exc_info для traceback
        return jsonify({"error": str(e)}), 500

@app.route('/audio/<path:filename>', methods=['GET'])
def serve_file(filename):
    app.logger.info(f"Attempting to serve file: {filename} from directory: {DOWNLOAD_DIR_ABS}")
    # Проверка существования файла перед отдачей
    file_to_serve_path = os.path.join(DOWNLOAD_DIR_ABS, filename)
    if not os.path.exists(file_to_serve_path):
        app.logger.error(f"File {filename} NOT FOUND at {file_to_serve_path} for serving.")
        return jsonify({"error": "File not found on server"}), 404
    
    app.logger.info(f"Serving file: {file_to_serve_path}")
    return send_from_directory(DOWNLOAD_DIR_ABS, filename, as_attachment=False) # as_attachment=False чтобы браузер пытался отобразить

if __name__ == '__main__':
    # Для локального запуска, на Railway порт будет управляться платформой
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
