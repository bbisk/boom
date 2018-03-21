from django.contrib import admin
from app.models import Booking, Room, RoomUser, Equipment

admin.site.register(Room)
admin.site.register(Booking)
admin.site.register(RoomUser)
admin.site.register(Equipment)
