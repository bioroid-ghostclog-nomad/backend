from django.urls import path
from . import views

urlpatterns = [
    path("chatingroom", views.ChatingRoomData.as_view(), name="ChatingRoom"),
    path("<int:id>/messages", views.ChatingMessages.as_view(), name="ChatingMessages"),
]
