from django.urls import path
from . import views

urlpatterns = [
    path("chatingroom", views.ChatingRoomData.as_view(), name="ChatingRoom"),
    path("chatingrooms", views.ChatingRooms.as_view(), name="ChatingRooms"),
    path("stats", views.Stats.as_view(), name="Stats"),
    path("<int:id>/messages", views.ChatingMessages.as_view(), name="ChatingMessages"),
]
