# services/biometrics.py
import base64
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
from users.models import TrainTicket, BiometricProfile, User
import os
import logging

# Путь к файлу каскада Хаара для обнаружения лиц
HAAR_CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

# Инициализация распознавателя лиц LBPH
recognizer = cv2.face.LBPHFaceRecognizer_create()

# Путь к файлу модели распознавания
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'face_model.yml')

def train_recognizer():
    """Тренирует распознаватель на основе сохраненных лиц."""
    faces = []
    labels = []
    biometric_profiles = BiometricProfile.objects.all()

    for profile in biometric_profiles:
        # Путь к изображению лица
        face_image_path = profile.face_image.path
        image = cv2.imread(face_image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            continue
        
        face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)
        faces_rects = face_cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5)
        
        for (x, y, w, h) in faces_rects:
            face = image[y:y+h, x:x+w]
            faces.append(face)
            labels.append(profile.user.id)  # Используем ID пользователя как метку

    if faces and labels:
        recognizer.train(faces, np.array(labels))
        recognizer.save(MODEL_PATH)

def recognize_face(photo_data, cruise_id):
    """
    Разпознает лицо на фото и возвращает информацию о пользователе или статус.
    """
    try:
        # Декодируем изображение из base64
        image_data = base64.b64decode(photo_data.split(',')[1])
        image = Image.open(BytesIO(image_data)).convert('L')  # Преобразовать в оттенки серого

        image_np = np.array(image)
        
        face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)
        faces_rects = face_cascade.detectMultiScale(image_np, scaleFactor=1.1, minNeighbors=5)

        if len(faces_rects) == 0:
            return 0  # На фото нет лиц

        # Предполагаем, что на фото одно лицо
        (x, y, w, h) = faces_rects[0]
        face = image_np[y:y+h, x:x+w]

        # Тренируем распознающий модуль перед распознаванием
        if not os.path.exists(MODEL_PATH):
            train_recognizer()

        recognizer.read(MODEL_PATH)
        label, confidence = recognizer.predict(face)

        # Определение, насколько уверены в распознавании
        if confidence < 50:  # Порог можно настроить
            try:
                user = User.objects.get(id=label)
                # Проверяем, имеет ли пользователь билет на текущий рейс
                ticket = TrainTicket.objects.filter(train_id=cruise_id, user=user).last()
                if ticket:
                    return {
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'seat_number': ticket.seat_number
                    }
                else:
                    return 1  # Лицо распознано, но нет билета на рейс
            except User.DoesNotExist:
                return 1  # Лицо распознано, но пользователь не найден
        else:
            return 1  # Лицо не распознано с достаточной уверенностью

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка при распознавании лица: {e}")
        return 0
