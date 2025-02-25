import face_recognition
import base64
from io import BytesIO
from PIL import Image
import numpy as np
from users.models import TrainTicket, TrainInfo



def recognize_face(photo_data, cruise_id):
    """Вернет 0 если на фото нет лиц, 1 если лица нет в базе рейса, {first_name, last_name, seat_number} если пассажир найден"""
    image_data = base64.b64decode(photo_data.split(',')[1])
    image = Image.open(BytesIO(image_data))

    # Конвертируем в RGB перед сохранением
    if image.mode != 'RGB':
        image = image.convert('RGB')
        
    # Поворачиваем изображение на 180 градусов
    image = image.rotate(180)


    image_np = np.array(image)
    face_encodings = face_recognition.face_encodings(image_np)

    if face_encodings:
        face_encoding = face_encodings[0]

        # Получение всех билетов для текущего рейса
        tickets = TrainTicket.objects.all()

        for ticket in tickets:
            # Проверяем, если face_data не пустой
            if ticket.face_data:
                known_face_encoding = np.frombuffer(ticket.face_data, dtype=np.float64)
                results = face_recognition.compare_faces([known_face_encoding], face_encoding, tolerance=0.5)

                if results[0]:
                    return {
                        'user_name': ticket.user_name,
                        'seat_number': ticket.seat_number
                    }

        return 1

    return 0
