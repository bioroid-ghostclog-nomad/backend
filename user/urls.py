from django.urls import path
from . import views

urlpatterns = [
    path('regist/', views.Regist.as_view(), name='regist'),
]