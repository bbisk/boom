from django.db import models


class Room(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=64)
    capacity = models.SmallIntegerField()
    equipment = models.ManyToManyField('Equipment')


class Booking(models.Model):
    booking_date = models.DateField()
    room_id = models.ForeignKey(Room)
    comment = models.TextField()
    room_user = models.ForeignKey('RoomUser', null=True)


class RoomUser(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=64)
    comment = models.TextField(null=True)

class Equipment(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=64)