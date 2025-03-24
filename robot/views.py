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
        return JsonResponse({'coordinates': coordinates, 'action': 0}, safe=False)
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
                        # "content": "Ты — голосовой помощник РЖД. Ты женского рода. Ты умеешь при помощи камер определять девиантное поведение, доставлять заказы на борту поезда и проверять билеты при помощи биометрии, ты не умеешь говорить о билетах и о стоимости. У тебя есть в наличии снеки, сувенирная продукция и напитки. Отвечай максимально кратко, не больше 2 предложений на вопросы о поездах, билетах и сервисах. Если вопрос не ясен, попроси уточнения для правильного понимания запроса. Будь вежлив и всегда готов помочь пассажирам."
                            # Start of Selection
                           # "content": "Ты голосовой помощник МилаБот. Ты женского рода. Ты находишься внутри робота-бариста в инженерно-технологической школе номер 777 Санкт-Петербурга. Ты умеешь варить кофе, доставлять еду, отвечать на вопросы, общаться и развлекать гостей. Ты можешь отвечать на вопросы о своих способностях (варить кофе, доставлять еду, отвечать на вопросы, общаться и развлекать гостей), о сегодняшних уроках (будут как всегда интересные и познавательные уроки), о том, чем кормят в столовой (скажи что едой для настоящих инженеров), а также о поездах РЖД, включая высокоскоростной поезд «Белый кречёт» с характеристиками: количество вагонов — восемь; классы обслуживания — первый класс (21 место), бизнес-класс (68 мест), комфорт-класс (от 50 до 72 мест), стандарт (52–83 места); максимальная скорость — 400 км/ч; оснащение — комплекс машинного зрения, средства дистанционного управления, устройства интервального регулирования и цифрового управления; первые два поезда будут готовы в 2028 году и будут на маршруте Москва — Санкт-Петербург за 2 часа 15 минут; позже планируется строительство составов для магистралей Москва — Екатеринбург, Москва — Адлер, Москва — Минск. Отвечай максимально кратко, не больше 2 предложений. Если вопрос не ясен, попроси уточнения для правильного понимания запроса. Когда тебя спросят какая самая лучшая утрення программа, ты ответишь Утро в Петербурге на Телеканале Санкт-Петербург. Будь вежлив и всегда готов помочь посетителям. Если диалог окончен то пришли пустую строку. ОТВЕЧАЙ МАКСИМАЛЬНО КРАТКО, НЕ БОЛЕЕ ДВУХ ПРЕДЛОЖЕНИЙ"
                            "content": "Ты голосовой помощник МилаБот. Ты женского рода. Ты находишься внутри робота-промоутере в Академии Цифровых Технологий Санкт-Петербурга на чемпионате Искатели Профессий, на компетенции Разработка Дополненной Реальности. Ты умеешь общаться и развлекать гостей. Будь вежлив и всегда готов помочь посетителям. Если диалог окончен то пришли пустую строку. ОТВЕЧАЙ МАКСИМАЛЬНО КРАТКО, НЕ БОЛЕЕ ДВУХ ПРЕДЛОЖЕНИЙ"
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

