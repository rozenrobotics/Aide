import json
import urllib.request
import urllib.parse

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from yoomoney import Quickpay, Client
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from multimedia.models import UserOrder, Product
from django.contrib.auth.decorators import login_required
import uuid
from RobotStuartRzd.keys import youmoney_token
from robot.send_to_robot import procces_order
from users.models import User, TrainTicket
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



class RobotAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        # Инициализируем переменные для хранения значений
        self.deviant = None
        self.lidar = None

    def get_deviant_value(self):
        """
        Получить значение места работы робота
        """
        try:
            response = self.session.get(f"https://172.20.10.5:8001/conditions/get_deviant_value")
            data = response.json()
            self.deviant = data.get('deviant')
            return self.deviant

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении значения места работы робота: {e}")
            return None
    def get_lidar_value(self):
        """
        Получить значение места работы робота
        """
        try:
            response = self.session.get(f"https://172.20.10.5:8001/conditions/get_lidar_value")
            data = response.json()
            self.lidar = data.get('lidar')
            return self.lidar

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении значения места работы робота: {e}")
            return None



@login_required(login_url='login')
def create_payment(request, product):
    user = request.user
    label = str(uuid.uuid4())  # Генерация уникальной метки

    sum = Product.objects.get(id=product).price

    quickpay = Quickpay(
        receiver="4100118786548312",
        quickpay_form="shop",
        targets="Покупка на Портале ВСМ",
        paymentType="AC",  # Тип оплаты (AC — с карты, PC — из кошелька)
        sum=sum,  # Цена товара
        label=label,
        successURL=request.build_absolute_uri('/multimedia/check-payment-status/')
    )

    # Сохранение подписки с пометкой
    order = UserOrder.objects.create(
        user=user,
        yoomoney_label=label,
        product=Product.objects.get(id=product),
        seat_number=TrainTicket.objects.filter(user=user).last().seat_number,

    )

    return redirect(quickpay.redirected_url)


@login_required(login_url='login')
def check_payment_status(request):
    user = request.user
    order = UserOrder.objects.filter(user=user, is_active=False).last()
    token = youmoney_token  # Замените на ваш токен
    client = Client(token)
    try:
        # Проверка операции с использованием метки
        history = client.operation_history(label=order.yoomoney_label)
        if history.operations:
            operation = history.operations[0]
            if operation.status == 'success':
                # Если оплата успешна, активируйте подписку
                order.is_active = True
                order.save()
                procces_order(order, TrainTicket.objects.filter(user=user).last().seat_number)  # запрос к роботу
                return render(request, 'multimedia/success.html')
    except:
        pass

    return render(request, 'multimedia/failure.html')


@login_required(login_url='login')
def product_list(request):
    products = Product.objects.all()
    return render(request, 'multimedia/product_list.html', {'products': products})


@login_required(login_url='login')
def multimedia_index(request):
    best_product = Product.objects.first()
    return render(request, 'multimedia/multimedia_index.html', {'best_product': best_product})


@login_required(login_url='login')
def films(request):
    return render(request, 'multimedia/films.html')


@login_required(login_url='login')
def music(request):
    return render(request, 'multimedia/music.html')


@login_required(login_url='login')
def gpt(request):
    return render(request, 'multimedia/gpt.html')


@login_required(login_url='login')
@csrf_exempt
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
                        "content": "Ты - виртуальный проводник РЖД. Ты помогаешь пассажирам с вопросами о поездах, билетах и сервисах РЖД. Ты знаешь все правила проезда в поездах, можешь подсказать, как купить билет, рассказать о услугах в поезде и на вокзале. Ты всегда вежлив и готов помочь пассажирам с любыми вопросами, связанными с поездками по железной дороге."
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


@login_required(login_url='login')
def test_payment(request, product):
    user = request.user
    # Генерируем уникальную метку для заказа
    label = str(uuid.uuid4())

    product_obj = get_object_or_404(Product, id=product)
    order = UserOrder.objects.create(
        user=user,
        yoomoney_label=label,
        product=product_obj
    )
    # Симулируем мгновенную оплату: помечаем заказ как активный
    order.is_active = True
    order.save()

    # Если у пользователя уже есть билет, передаём номер места в робота
    train_ticket = TrainTicket.objects.filter(user=user).last()
    if train_ticket:
        procces_order(order, train_ticket.seat_number)
    # Отображаем страницу успешной оплаты
    return render(request, 'multimedia/success.html')

@csrf_exempt
def get_all_orders(request):
    orders = UserOrder.objects.filter(is_done=False)
    orders_data = [{
        'is_take_in_robot': order.is_take_in_robot,
        'seat': order.seat,
    } for order in orders]
    return JsonResponse({'orders': orders_data}, status=200)

@csrf_exempt
def end_order(request, seat):
    orders = UserOrder.objects.filter(is_done=False, seat=seat)
    for order in orders:
        order.is_done = True
        order.save()
    return JsonResponse({'status': 'success'}, status=200)

def stuart(request):
    return render(request, 'multimedia/stuart.html')


@csrf_exempt
def get_data(request):
    orders = UserOrder.objects.filter(is_done=False, is_take_in_robot=False)
    orders_data = []
    for order in orders:
        orders_data.append({
            'name': order.product.name,
            'status': order.is_take_in_robot,
            'order_id': order.id,
        })


    return JsonResponse({
        'orders': orders_data,
        'is_alert': RobotAPI().get_deviant_value(),
        'is_stopped': RobotAPI().get_lidar_value() == 2,
    }, status=200)

@csrf_exempt
def take_order_in_robot(request, order_id):
    order = UserOrder.objects.get(id=order_id)
    order.is_take_in_robot = True
    order.save()
    return JsonResponse(status=200)
