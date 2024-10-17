from django.urls import path
from . import views

urlpatterns = [
    path('userdata/', views.UserData.as_view(), name='UserData'),
    path('Idchk/', views.IdChk.as_view(), name='IdChk'),
]