import json
import urllib.request
import urllib.parse

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

            # Отправка запроса на AI-сервис с использованием urllib
            ai_url = 'https://foteapi2.pythonanywhere.com/process'
            headers = {'Content-Type': 'application/json'}
            payload = json.dumps({'request_type': 'rzd_question_answering', 'text': question}).encode('utf-8')

            req = urllib.request.Request(ai_url, data=payload, headers=headers)
            with urllib.request.urlopen(req) as response:
                response_data = json.loads(response.read().decode('utf-8'))

            return JsonResponse({'response': response_data})

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

