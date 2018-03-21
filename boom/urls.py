from django.conf.urls import url
from django.contrib import admin

from app.views import RoomView, RoomDeleteView, RoomsView, EditRoomView, \
    AddRoomView, AddBookingView, AddUserView, UserSetView, AddEquipmentView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', RoomsView.as_view(), name="rooms_view"),
    url(r'^(?P<slug>\w*(search))/', RoomsView.as_view(), name="search_view"),
    url(r'^room/new/$', AddRoomView.as_view(), name="add_room"),
    url(r'^room/modify/(?P<id>(\d)+)/$', EditRoomView.as_view(), name="room_edit"),
    url(r'^room/delete/(?P<id>(\d)+)/$', RoomDeleteView.as_view(), name="room_delete"),
    url(r'^room/(?P<id>(\d)+)/$', RoomView.as_view(), name="room_view"),
    # url(r'^reservation/(?P<id>(\d)+)/$', AddBookingView.as_view(), name="room_view"),
    url(r'^book/$', AddBookingView.as_view(), name="book"),
    url(r'^user/add/$', AddUserView.as_view(), name="add_user"),
    url(r'^user/set/(?P<userid>(\d)+)/$', UserSetView.as_view(), name="set_user"),
    url(r'^equipment/add/$', AddEquipmentView.as_view(), name="add_equipment"),

]
