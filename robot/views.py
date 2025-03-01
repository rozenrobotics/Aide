import base64

from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import escape
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from users.models import TrainTicket
from services.biometrics import recognize_face
from users.models import TrainInfo
from users.syncdb import sync_train_data
from robot.functions.cv import recognize_face_cords
import json
import urllib.request
import urllib.parse
from services.deviant import recognize_action


def departure_index(request):
    sync_train_data()
    cruise = TrainInfo.objects.first()
    return (render(request, 'robot/departure.html', context={'cruise': cruise}))


def recognize_face_ajax(request):
    if request.method == 'POST':
        photo_data = request.POST.get('photo_data')
        cruise_id = TrainInfo.train_number

        if photo_data:
            recognize_result = recognize_face(photo_data, cruise_id)
            print(recognize_result)
            if recognize_result == 0:
                return JsonResponse({'status': 'no_face'})
            elif recognize_result == 1:
                return JsonResponse({'status': 'not_registered'})
            else:
                return JsonResponse({'status': 'success', 'data': recognize_result})
    return JsonResponse({'status': 'error', 'message': 'Некорректный запрос.'})


def routine(request):
    return (render(request, 'robot/routine.html'))


def recognize_face_cords_ajax(request):
    if request.method == 'POST':
        # Проверьте, что содержимое запроса является JSON
        if request.content_type != 'application/json':
            return JsonResponse({'error': 'Content-Type must be application/json'}, status=400)

        # Попробуйте загрузить JSON из тела запроса
        data = json.loads(request.body.decode('utf-8'))
        photo_data = data.get('photo_data')

        if not photo_data:
            return JsonResponse({'error': 'No photo data provided'}, status=400)

        # Декодирование Base64 строки
        image_data = base64.b64decode(photo_data)
        coordinates = recognize_face_cords(image_data)
        action = recognize_action(image_data)
        print(action)
        return JsonResponse({'coordinates': coordinates, 'action': action}, safe=False)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def process_question_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get('text', '')

            # Отправка запроса на AI-сервис
            ai_url = ' http://api.freil.ru/generate'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': '4Ikp8h-YohTlxJtAhquvveS0LjfTnh0fVK4R0S-YZek'
            }
            payload = {
                "api_key": "RiV544NRwNLTcH8rLIAefu2_ffCHAVRfFwtgnmikwkY",
                "model": "llama-3.3-70b-versatile", 
                "model_key": "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",
                "messages": [
                    {
                        "role": "system",
                        "content": "Ты — голосовой помощник РЖД. Ты женского рода. Ты умеешь при помощи камер определять девиантное поведение, доставлять заказы на борту поезда и проверять билеты при помощи биометрии, ты не умеешь говорить о билетах и о стоимости. У тебя есть в наличии снеки, сувенирная продукция и напитки. Отвечай максимально кратко, не больше 2 предложений на вопросы о поездах, билетах и сервисах. Если вопрос не ясен, попроси уточнения для правильного понимания запроса. Будь вежлив и всегда готов помочь пассажирам."
                    },
                    {
                        "role": "user", 
                        "content": question
                    }
                ],
                "temperature": 1,
                "max_tokens": 1024,
                "top_p": 1,
                "stream": False,
                "stop": None
            }

            req = urllib.request.Request(
                ai_url,
                data=json.dumps(payload).encode('utf-8'),
                headers=headers
            )
            with urllib.request.urlopen(req) as response:
                response_data = json.loads(response.read().decode('utf-8'))

            return JsonResponse({'response': response_data['answer']})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Произошла ошибка при генерации ответа'}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)

