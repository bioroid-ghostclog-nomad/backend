from django.urls import path
from . import views

urlpatterns = [
    path("chatingroom", views.ChatingRoomData.as_view(),name="ChatingRoom"),
]
