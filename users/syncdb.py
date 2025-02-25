import base64
import requests
import urllib3
from django.conf import settings
from users.models import TrainTicket, TrainInfo
from urllib3.exceptions import InsecureRequestWarning


def sync_train_data():
    """
    Синхронизация данных поезда и билетов из удаленного сервера.
    Обновляет запись в модели TrainInfo и создает новые записи в TrainTicket.
    """
    urllib3.disable_warnings(InsecureRequestWarning)

    # Получение номера поезда из настроек
    train_number = settings.TRAIN_NUMBER
    SERVER_URL = f'https://{settings.LOCAL_SERVER_URL}/users/api/get_train_data/{train_number}/'

    try:
        response = requests.get(SERVER_URL, verify=False)
        response.raise_for_status()  # Выбросит исключение для статусов ошибок (4xx, 5xx)
        data = response.json()

        # Обновление информации о поезде
        TrainInfo.objects.update_or_create(
            train_number=data['train_number'],
            defaults={
                'departure_station': data['departure_station'],
                'arrival_station': data['arrival_station'],
                'departure_time': data['departure_time'],
                'arrival_time': data['arrival_time']
            }
        )

        # Очистка текущих данных по билетам
        TrainTicket.objects.all().delete()

        # Создание записей о билетах
        for ticket_data in data['tickets']:
            # Декодирование face_data из Base64 обратно в бинарный формат
            face_data_decoded = base64.b64decode(ticket_data['face_data']) if ticket_data['face_data'] else None

            TrainTicket.objects.create(
                user_id=ticket_data['user_id'],
                user_name=ticket_data['user_name'],
                face_data=face_data_decoded,
                seat_number=ticket_data['seat_number'],
                created_at=ticket_data['created_at'],
            )

        print(f"Синхронизация данных для поезда {train_number} завершена успешно.")

    except requests.RequestException as e:
        print(f"Ошибка при запросе данных с сервера: {e}")

    except ValueError as e:
        print(f"Ошибка обработки данных: {e}")

    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
