import json
from django.http import JsonResponse
from django.shortcuts import render
from conditions import send_to_robot
from conditions.send_to_robot import process_order, start_talking, stop_talking
from django.views.decorators.csrf import csrf_exempt

Is_lidar = 0
IS_ROBOT_TALKING = False
IS_ROBOT_WORK_IN_TRAIN = False
IS_DEVIANT = False

def set_deviant(deviant):
    global IS_DEVIANT
    IS_DEVIANT = deviant

@csrf_exempt
def start_talking_ajax(request):
    try:
        global IS_ROBOT_TALKING
        IS_ROBOT_TALKING = True
        return JsonResponse({'status': 'success'}, status=200)
    except:
        return JsonResponse({'error': 'Error'}, status=400)

@csrf_exempt
def stop_talking_ajax(request):
    try:
        global IS_ROBOT_TALKING
        IS_ROBOT_TALKING = False
        return JsonResponse({'status': 'success'}, status=200)
    except:
        return JsonResponse({'error': 'Error'}, status=400)


@csrf_exempt
def get_speaking_value(request):
    global IS_ROBOT_TALKING
    return JsonResponse({'is_robot_talk': IS_ROBOT_TALKING}, status=200)

@csrf_exempt
def get_place_value(request):
    global IS_ROBOT_WORK_IN_TRAIN
    return JsonResponse({'is_robot_work_in_train': IS_ROBOT_WORK_IN_TRAIN}, status=200)

@csrf_exempt
def set_lidar_value(request, is_lidar):
    global Is_lidar
    Is_lidar = is_lidar
    print(Is_lidar)
    return (JsonResponse({'status': 'success'}, status=200))

@csrf_exempt
def get_deviant_value(request):
    global IS_DEVIANT
    x = IS_DEVIANT
    IS_DEVIANT = False
    return (JsonResponse({'deviant': x}, status=200))

@csrf_exempt
def get_lidar_value(request):
    global Is_lidar
    return JsonResponse({'lidar': Is_lidar}, status=200)



