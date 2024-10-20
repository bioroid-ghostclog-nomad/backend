from django.urls import path
from . import views

urlpatterns = [
    path("me", views.Me.as_view()),
    path("password", views.UserPassword.as_view()),
    path("userdata", views.UserData.as_view(), name="UserData"),
    path("Idchk", views.IdChk.as_view(), name="IdChk"),
    path("email", views.Email.as_view(), name="Email"),
    path("apikey", views.APIKey.as_view(), name="APIKey"),
]
