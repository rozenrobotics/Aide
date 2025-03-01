from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

from users.models import TrainTicket, BiometricProfile, TrainCruise, RobotProfile, TicketOrder


@admin.register(TrainCruise)
class TrainCruiseAdmin(admin.ModelAdmin):
    list_display = (
        'train_number', 'departure_station', 'arrival_station', 'departure_time', 'arrival_time'
    )
    search_fields = ('train_number', 'departure_station', 'arrival_station')
    list_filter = ('departure_station', 'arrival_station', 'departure_time')
    ordering = ('-departure_time',)
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('train_number', 'departure_station', 'arrival_station', 'departure_time', 'arrival_time')
        }),
        ('Дополнительная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )


@admin.register(TrainTicket)
class TrainTicketAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'train', 'seat_number', 'get_departure_station', 'get_arrival_station', 'get_departure_time',
        'get_arrival_time'
    )
    search_fields = ('train__train_number', 'train__departure_station', 'train__arrival_station', 'user__username')
    list_filter = ('train__departure_station', 'train__arrival_station', 'train__departure_time')
    ordering = ('-train__departure_time',)
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('user', 'train', 'seat_number')
        }),
        ('Дополнительная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    def get_departure_station(self, obj):
        return obj.train.departure_station

    get_departure_station.short_description = 'Станция отправления'

    def get_arrival_station(self, obj):
        return obj.train.arrival_station

    get_arrival_station.short_description = 'Станция прибытия'

    def get_departure_time(self, obj):
        return obj.train.departure_time

    get_departure_time.short_description = 'Время отправления'

    def get_arrival_time(self, obj):
        return obj.train.arrival_time

    get_arrival_time.short_description = 'Время прибытия'


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'is_staff')



admin.site.register(RobotProfile)
admin.site.register(TicketOrder)


@admin.register(BiometricProfile)
class BiometricProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'face_image')
