from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from datetime import datetime
from django.urls.base import reverse_lazy
from django.views.generic.base import View

from app.models import Room, Booking, Equipment, RoomUser

TEMPLATE = "booking.html"

# Supporting classes
class Cookie:
    @staticmethod
    def user_cookie(request):
        if "user_id" in request.COOKIES:
            user = RoomUser.objects.get(id=request.COOKIES.get('user_id'))
            user_detials = [(user.id, user.name)]
            return user_detials
        else:
            return None

class GetRoom():
    @staticmethod
    def get_room(id):
        room = Room.objects.get(id=id)
        return room

    @staticmethod
    def booked_rooms(date):
        booked_rooms = [bkg.room_id_id for bkg in Booking.objects.filter(booking_date=date)]
        return booked_rooms

    @staticmethod
    def get_available_room(filter):
        room = Room.objects.filter(**filter)
        return room


class GetUser():
    @staticmethod
    def get_user():
        user = RoomUser.objects.all()
        return user

#View classes
class RoomsView(View):
    room_booked = GetRoom.booked_rooms(datetime.now().date())
    rooms_booked = GetRoom.get_available_room({'id__in':room_booked})

    def get(self, request, slug=""):
        user_list = GetUser.get_user()
        context = {
            'users': user_list,
            'cookie': Cookie.user_cookie(request)
        }

        if slug == "search":
            equipment_list = Equipment.objects.all()
            context['search'] = True
            context['equipments'] = equipment_list

        else:
            if request.GET:
                name = request.GET.get('name')
                capacity = request.GET.get('capacity')
                equipment = request.GET.getlist('equipment')
                booking_date = request.GET.get('date')
                # room_booked = GetRoom.booked_rooms(datetime.now().date())
                search_filter = {
                    'name__icontains': name
                }

                if booking_date:
                    self.room_booked = GetRoom.booked_rooms(booking_date)

                    dt = datetime.strptime(booking_date, '%Y-%m-%d')
                    if dt.date() < datetime.now().date():
                        context['error'] = "The date picked is from the past. Please try again."

                if capacity:
                    search_filter['capacity__gte'] = int(capacity)

                rooms = GetRoom.get_available_room(search_filter)

                if equipment:
                    for i, equipment_id in enumerate(equipment):
                        if i == 0:
                            rooms = rooms.filter(equipment=equipment_id)
                        elif i >= 1:
                            rooms = rooms and rooms.filter(equipment=equipment_id)

                self.rooms_booked = rooms.filter(id__in=self.room_booked)
                rooms = rooms.exclude(id__in=self.room_booked)
                if not rooms:
                    context['error'] = "Sorry. No rooms matching criteria available on this day."

            else:
                rooms = GetRoom.get_available_room({}).exclude(id__in=self.room_booked)

            context['rooms'] = rooms
            context['rooms_booked'] = self.rooms_booked

        return render(request, TEMPLATE, context)


class RoomView(View):
    def get(self, request, id):
        room = GetRoom.get_room(id)
        users = RoomUser.objects.all()
        room_equipment = room.equipment.all()
        booked_on = Booking.objects.filter(room_id=id)
        booked_dates = [day.booking_date for day in booked_on if day.booking_date >= datetime.now().date()]
        context = {
            'room_view': room,
            'room_equipment': room_equipment,
            'booked': booked_dates,
            'users': users,
            'cookie': Cookie.user_cookie(request)
        }
        return render(request, TEMPLATE, context)


class RoomDeleteView(View):
    def get(self, request, id):
        room = GetRoom.get_room(id)
        room.delete()
        context = {
            'notice': "Room has been deleted.",
            'cookie': Cookie.user_cookie(request)
        }
        return render(request, TEMPLATE, context)


class UserSetView(View):
    def get(self, request, userid):
        response = HttpResponseRedirect(reverse_lazy('rooms_view'))
        response.set_cookie('user_id', userid)
        return response

#Form generetor classes
class AddFormView(View):
    fields = None
    temp = None
    model = None
    select_model = None
    success_url = None
    models = None

    def get_object(self, **kwargs):
        for key, value in kwargs.items():
            if key == "obj_id":
                object = self.models['model'].objects.get(id=value)
                return object

            if key == "input_type":
                object = self.models[value].objects.all()
                return object

    def get_context_data(self, field_name, input_type, label, value, value_list, context):
        value_list.append((field_name, input_type, value, label))

        if input_type == "select" or input_type == "select_multi":
            select_all = self.get_object(input_type=input_type)
            context['select_all'] = select_all

        if input_type == "select_user":
            select_all = self.get_object(input_type=input_type)
            context['select_more'] = select_all
        context['model'] = value_list
        return context

    def get(self, request):
        value = ""
        value_list = []
        context = {}
        for field_name, input_type, label in self.fields:
            context = self.get_context_data(field_name, input_type, label, value, value_list, context)
        context['cookie'] = Cookie.user_cookie(request)
        return render(request, self.temp, context)

    def post(self, request):
        model_dict = {}
        value_select = []
        for field_name, input_type, label in self.fields:
            if input_type == "select" or input_type == "select_multi":
                value_select = request.POST.getlist(field_name)
            else:
                value = request.POST.get(field_name)
                model_dict[field_name] = value

        obj_create = self.models['model'].objects.create(**model_dict)
        if value_select:
            getattr(obj_create, field_name).set(value_select)
        return redirect(self.success_url)


class EditFormView(AddFormView):
    def get(self, request, id):
        model_get = super().get_object(obj_id=id)
        value_list = []
        context = {}
        for field_name, input_type, label in self.fields:
            value = getattr(model_get, field_name)
            context = super().get_context_data(field_name, input_type, label, value, value_list, context)
        context['cookie'] = Cookie.user_cookie(request)
        return render(request, self.temp, context)

    def post(self, request, id):
        model_get = super().get_object(obj_id=id)
        for field_name, input_type, label in self.fields:
            if input_type == "select" or input_type == "select_multi":
                value = request.POST.getlist(field_name)
            else:
                value = request.POST.get(field_name)
            setattr(model_get, field_name, value)
            model_get.save()
        return redirect(self.success_url)


class BookingFormView(AddFormView):
    def post(self, request):
        context = {}
        db_model = ['booking_date', 'room_id', 'comment', 'room_user']
        input_values = [value for value in request.POST.values()]
        model_dict = dict(zip(db_model, input_values))
        booked_date = request.POST.get('booking_date')
        room_to_check = model_dict['room_id']
        existing_booking = Booking.objects.filter(booking_date=booked_date, room_id=room_to_check)
        if existing_booking:
            context['error'] = "This room is already booked on the selected date."
            return render(request, TEMPLATE, context)
        else:
            model_dict['room_id'] = Room.objects.get(id=model_dict['room_id'])
            model_dict['room_user'] = RoomUser.objects.get(id=model_dict['room_user'])
            self.models['model'].objects.create(**model_dict)
            return redirect(self.success_url)

#Classes building forms
class AddBookingView(BookingFormView):
    fields = [
              ('booking_date', 'date', 'Date'),
              ('name', 'select', 'Room name'),
              ('comment', 'text', 'Comment'),
              ('name', 'select_user', 'User'),
              ]
    models = {
        'model': Booking,
        'select': Room,
        'select_user' : RoomUser
    }
    temp = "form.html"
    success_url = reverse_lazy('rooms_view')


class AddRoomView(AddFormView):
    fields = [('name', 'text', 'Room name'),
              ('capacity', 'number', 'Room capacity'),
              ('equipment', 'select_multi', 'Equipment')]
    models = {
        'model': Room,
        'select_multi': Equipment
    }
    temp = "form.html"
    success_url = reverse_lazy('rooms_view')


class EditRoomView(EditFormView):
    fields = [('name', 'text', 'Room name'),
              ('capacity', 'number', 'Room capacity'),
              ('equipment', 'select_multi', 'Equipment')]
    models = {
        'model': Room,
        'select_multi': Equipment
    }
    temp = "form.html"
    success_url = reverse_lazy('rooms_view')


class AddUserView(AddFormView):
    fields = [('name', 'text', 'User name'),
              ('comment', 'text', 'Comment'),
                ]
    models = {
        'model': RoomUser
    }
    temp = "form.html"
    success_url = reverse_lazy('rooms_view')


class AddEquipmentView(AddFormView):
    fields = [('name', 'text', 'Item name'),
                ]
    models = {
        'model': Equipment
    }
    temp = "form.html"
    success_url = reverse_lazy('rooms_view')

