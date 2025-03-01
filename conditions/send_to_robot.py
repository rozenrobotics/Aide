import json
import urllib.request
import urllib.parse

from RobotStuartDjangoRobot import settings

is_talking_now = False


def process_order(data):
    order_id = data.get('order_id')
    product_id = data.get('product_id')
    product_name = data.get('product_name')
    product_category = data.get('product_category')
    seat_id = data.get('seat_id')
    print(order_id, product_id, product_name, product_category, seat_id)

    


def start_talking():
    global is_talking_now
    if is_talking_now:
        return
    is_talking_now = True

    url = f'http://{settings.ROBOT_MALINA_SERVER_URL}/start_talking'
    try:
        with urllib.request.urlopen(url) as response:
            print("Switch to start talk!")
    except urllib.error.URLError as e:
        print(f"Error during GET request: {e}")


def stop_talking():
    global is_talking_now
    if not is_talking_now:
        return
    is_talking_now = False

    url = f'http://{settings.ROBOT_MALINA_SERVER_URL}/stop_talking'
    try:
        with urllib.request.urlopen(url) as response:
            print("Switch to stop talk!")
    except urllib.error.URLError as e:
        print(f"Error during GET request: {e}")
