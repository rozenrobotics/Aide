# services/biometrics.py
import face_recognition
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import json


from users.models import BiometricProfile, TrainTicket


def register_face(photo_data, user):
    # Декодирование изображения из base64
    image_data = base64.b64decode(photo_data.split(',')[1])
    image = Image.open(BytesIO(image_data))

    # Преобразование изображения в формат RGB (если необходимо)
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Преобразование изображения в формат numpy
    image_np = np.array(image)
    # Поиск лиц на изображении
    face_encodings = face_recognition.face_encodings(image_np)

    if face_encodings:
        face_encoding = face_encodings[0].tolist()  # Преобразуем в list (Python-совместимый тип)
        bio_entry, created = BiometricProfile.objects.get_or_create(
            user=user,
            defaults={'face_data': json.dumps(face_encoding)}
        )
        if not created:
            bio_entry.face_data = json.dumps(face_encoding)
            bio_entry.save()

        return bio_entry.id  # Возвращаем ID записи в биометрической базе

    return None  # Если лицо не было найдено


def recognize_face(photo_data, cruise_id):
    """Вернет 0 если на фото нет лиц, 1 если лица нет в базе рейса, {first_name, last_name, seat_number} если пассажир найден"""
    image_data = base64.b64decode(photo_data.split(',')[1])
    image = Image.open(BytesIO(image_data))

    if image.mode != 'RGB':
        image = image.convert('RGB')

    image_np = np.array(image)
    face_encodings = face_recognition.face_encodings(image_np)

    if face_encodings:
        face_encoding = face_encodings[0]
        # Получение всех профилей пользователей с билетом на текущий рейс
        tickets = TrainTicket.objects.filter(train_id=cruise_id)
        users_with_tickets = [ticket.user for ticket in tickets]
        biometric_profiles = BiometricProfile.objects.filter(user__in=users_with_tickets)

        for entry in biometric_profiles:
            known_face_encoding = np.array(json.loads(entry.face_data))
            results = face_recognition.compare_faces([known_face_encoding], face_encoding, tolerance=0.6)

            if results[0]:
                return {'first_name': entry.user.first_name, 'last_name': entry.user.last_name,
                        'seat_number': TrainTicket.objects.filter(train_id=cruise_id,
                                                                  user=entry.user).last().seat_number}
        return 1

    return 0
