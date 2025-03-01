from datetime import timedelta
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta

from users.models import User


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('food', 'Еда'),
        ('souvenir', 'Сувенир'),
    ]
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)  # Поле для фото

    def __str__(self):
        return self.name


class UserOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    is_done = models.BooleanField(default=False)
    is_take_in_robot = models.BooleanField(default=False)
    seat = models.PositiveSmallIntegerField(default=1)
    yoomoney_label = models.CharField(max_length=255, unique=True)  # Уникальная метка для оплаты через YooMoney

    def __str__(self):
        return f"{self.user.username}"
