from datetime import datetime, timedelta
import logging
import os

def cleanup_logs(logs_path, days=30):
# Функция для удаления старых логов
    cutoff_date = datetime.now() - timedelta(days=days)
    for log_file in os.listdir(logs_path):
        log_file_path = os.path.join(logs_path, log_file)
        if os.path.isfile(log_file_path):
            file_creation_date = datetime.fromtimestamp(os.path.getctime(log_file_path))
            if file_creation_date < cutoff_date:
                os.remove(log_file_path)

# Создание папки для логов
script_dir = os.path.dirname(os.path.abspath(__file__))
logs_path = os.path.join(script_dir, "logs")
os.makedirs(logs_path, exist_ok=True)

# Установка имени файла логов
log_filename = datetime.now().strftime("czservice_%Y%m%d_%H%M%S.log")
log_filepath = os.path.join(logs_path, log_filename)

# Настройка логирования
logging.basicConfig(filename=log_filepath, level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

log = logging.getLogger('cz_service')