import requests



class RobotAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        # Инициализируем переменные для хранения значений
        self.is_robot_talk = None
        self.is_robot_work_in_train = None
        # Список для хранения заказов
        self.orders = []

    def get_order_values(self):
        """
        Получить список заказов и обновить их в классе
        """
        try:
            response = self.session.get(f"https://172.20.10.5:8000/multimedia/get_all_orders")
            data = response.json()

            # Обновляем список заказов
            self.orders = []
            for order in data.get('orders', []):
                self.orders.append({
                    'is_take_in_robot': order.get('is_take_in_robot'),
                    'seat': order.get('seat')
                })

            return self.orders

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении заказов: {e}")
            return None

    def get_speaking_value(self):
        """
        Получить значение флага разговора робота
        """
        try:
            response = self.session.get(f"https://172.20.10.5:8001/conditions/get_speaking_value")
            data = response.json()
            self.is_robot_talk = data.get('is_robot_talk')
            return self.is_robot_talk

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении значения разговора робота: {e}")
            return None

    def get_place_value(self):
        """
        Получить значение места работы робота
        """
        try:
            response = self.session.get(f"https://172.20.10.5:8001/conditions/get_place_value")
            data = response.json()
            self.is_robot_work_in_train = data.get('is_robot_work_in_train')
            return self.is_robot_work_in_train

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении значения места работы робота: {e}")
            return None
    def set_lidar_value(self, lidar_value):
        """
        Установить значение флага LIDAR, вызываешь если увидел препятствие впервые с 1, потом ждешь 15 секунд если
        препятствия нет то запускаешь с 0, если есть то уже с 2 и ждешь еще 45 секунд и если нет то 0, если есть то 3.
        потом просто стоишь мы тебя как-нибудь ребутним, например функцию напишем в классе которой чекать будешь можно
        ехать или нет
        """
        try:
            response = self.session.get(f"https://172.20.10.5:8001/conditions/set_lidar_value/{lidar_value}")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при установке значения LIDAR: {e}")
            return None
    def end_order(self, seat):
        """
        Завершить заказ для указанного места
        """
        try:
            response = self.session.get(f"https://172.20.10.5:8000/multimedia/end_order/{seat}")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при завершении заказа: {e}")
            return None


RobotAPI().set_lidar_value(0)