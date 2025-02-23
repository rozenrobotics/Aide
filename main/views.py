import uuid
import json
import urllib.request
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from users.models import TrainTicket, BiometricProfile
from services.biometrics import register_face, recognize_face
from django.urls import reverse
from yoomoney import Quickpay, Client
from django.conf import settings
from users.models import TrainCruise
from robot.send_to_robot import procces_order
from users.models import TicketOrder
from RobotStuartRzd.keys import youmoney_token


@login_required(login_url='login')
def index(request):
    return render(request, 'main/index.html')


@login_required(login_url='login')
def check_in(request):
    if request.method == 'POST':
        train_ticket_id = request.POST.get('train_ticket_id')
        photo_data = request.POST.get('photo_data')

        # Найти билет
        try:
            train_ticket = TrainTicket.objects.get(id=train_ticket_id, user=request.user)
        except TrainTicket.DoesNotExist:
            return HttpResponse("Билет не найден", status=404)

        if not BiometricProfile.objects.filter(user=request.user).exists():
            if photo_data:
                # Регистрация лица в биометрической базе
                if not register_face(photo_data, request.user):
                    return render(request, 'main/check_in.html',
                                  context={'error': "Ваше лицо не видно, попробуйте еще раз!"})
            else:
                return render(request, 'main/check_in.html', context={'error': "Вы не отсканировали лицо!"})

        return redirect('index')  # перенаправление на страницу успешной регистрации

    return render(request, 'main/check_in.html',
                  context={'is_bio': BiometricProfile.objects.filter(user=request.user).exists()})


def error(request):
    return render(request, 'main/error.html')


@login_required(login_url='login')
def purchase_ticket(request):
    """
    Форма для выбора рейса и указания места.
    Показывает только поезда со свободными местами.
    """
    if request.method == 'POST':
        try:
            train_id = request.POST.get('train_id')
            seat_number = request.POST.get('seat_number')
            train = get_object_or_404(TrainCruise, id=train_id)

            # Проверяем, не занято ли место
            if TrainTicket.objects.filter(train=train, seat_number=seat_number).exists():
                return render(request, 'main/purchase_ticket.html',
                              {'error': 'Это место уже занято. Пожалуйста, выберите другое.'})

            # Создаём заказ билета с фиксированной стоимостью и уникальной меткой
            label = str(uuid.uuid4())
            ticket_order = TicketOrder.objects.create(
                user=request.user,
                train_cruise=train,
                seat_number=seat_number,
                yoomoney_label=label
            )
            # Перенаправляем на страницу выбора способа оплаты
            return redirect('payment_options', order_id=ticket_order.id)
        except Exception as e:
            return render(request, 'main/failure_ticket.html',
                          {'error': str(e)})
    else:
        # Получаем все поезда
        trains = TrainCruise.objects.all()
        trains_with_seats = []

        for train in trains:
            # Получаем все занятые места для поезда
            occupied_seats = set(TrainTicket.objects.filter(train=train).values_list('seat_number', flat=True))
            # Создаем список свободных мест
            available_seats = [i for i in range(1, train.seat_count + 1) if i not in occupied_seats]

            if available_seats:  # Если есть свободные места
                train.available_seats = available_seats
                trains_with_seats.append(train)

        return render(request, 'main/purchase_ticket.html', {'trains': trains_with_seats})


@login_required(login_url='login')
def payment_options(request, order_id):
    """
    Страница, где пользователь выбирает способ оплаты.
    """
    ticket_order = get_object_or_404(TicketOrder, id=order_id, user=request.user)
    return render(request, 'main/payment_options.html', {'order': ticket_order})


@login_required(login_url='login')
def pay_ticket_yoomoney(request, order_id):
    """
    Инициализация оплаты через ЮМани.
    """
    ticket_order = get_object_or_404(TicketOrder, id=order_id, user=request.user)
    quickpay = Quickpay(
        receiver="4100118786548312",
        quickpay_form="shop",
        targets="Покупка билета на Портале ВСМ",
        paymentType="AC",
        sum=ticket_order.train_cruise.price,
        label=ticket_order.yoomoney_label,
        successURL=request.build_absolute_uri(reverse('pay_ticket_status', args=[ticket_order.id]))
    )
    return redirect(quickpay.redirected_url)


@login_required(login_url='login')
def pay_ticket_status(request, order_id):
    """
    Проверка статуса оплаты для заказа билета через ЮМани.
    После подтверждения оплаты билет отмечается как приобретённый.
    """
    ticket_order = get_object_or_404(TicketOrder, id=order_id, user=request.user)
    token = youmoney_token
    client = Client(token)
    try:
        history = client.operation_history(label=ticket_order.yoomoney_label)
        if history.operations:
            operation = history.operations[0]
            if operation.status == 'success':
                # Если оплата успешна, активируем заказ и отмечаем билет как приобретённый
                ticket_order.is_active = True
                ticket_order.save()
                train_ticket = TrainTicket.objects.create(
                    user=request.user,
                    train=ticket_order.train_cruise,
                    seat_number=ticket_order.seat_number
                )
                return render(request, 'main/success_ticket.html', {'ticket_order': ticket_order})
    except Exception as e:
        print(e)
        return render(request, 'main/failure_ticket.html', context={'error': str(e)})


@login_required(login_url='login')
def pay_ticket_test(request, order_id):
    """
    Тестовая оплата – отмечает заказ как оплачен без реального платежа.
    Билет сразу считается приобретённым.
    """
    ticket_order = get_object_or_404(TicketOrder, id=order_id, user=request.user)
    ticket_order.is_active = True
    ticket_order.save()
    train_ticket = TrainTicket.objects.create(
        user=request.user,
        train=ticket_order.train_cruise,
        seat_number=ticket_order.seat_number
    )
    return render(request, 'main/success_ticket.html', {'ticket_order': ticket_order})
