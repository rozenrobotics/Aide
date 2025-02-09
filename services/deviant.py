from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch
import io
from collections import deque

# Загрузка модели CLIP
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Очередь для хранения последних действий
action_history = deque(maxlen=5)

def recognize_action(image_data):
    """
    Распознает действие на изображении и определяет девиантное поведение
    Args:
        image_data: bytes - изображение в байтовом формате
    Returns:
        int - 1 если обнаружено устойчивое девиантное поведение, 0 если поведение нормальное
    """
    # Преобразование байтов в изображение
    image = Image.open(io.BytesIO(image_data))
    
    # Список возможных действий
    normal_actions = [
        "person is eating",
        "person is sitting", 
        "person is standing",
        "person is talking with other passengers",
        "person is walking through the train car"
    ]

    deviant_actions = [
        "person is smoking",
        "person is fighting",
        "person is harassing passengers",
        "person is making noise", 
        "person is littering",
        "person is carrying dangerous items",
        "person is threatening passengers",
        "person is climbing on seats"
    ]

    actions = normal_actions + deviant_actions

    # Подготовка данных
    inputs = processor(text=actions, images=image, return_tensors="pt", padding=True)

    # Получение прогнозов
    with torch.no_grad():
        outputs = model(**inputs)
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1)

    # Определение действия с наибольшей вероятностью
    predicted_action = actions[probs.argmax()]
    
    # Определяем тип действия (0 - нормальное, 1 - девиантное)
    is_deviant = 1 if predicted_action in deviant_actions else 0
    
    # Добавляем результат в историю
    action_history.append(is_deviant)
    
    # Проверяем историю на устойчивое девиантное поведение
    if len(action_history) == 4:
        deviant_count = sum(action_history)
        action_history.clear()
        # Возвращаем 1, если 4 или более действий девиантные (допуская одно нормальное)
        if deviant_count >= 3:
            return 1
            
    return 0
