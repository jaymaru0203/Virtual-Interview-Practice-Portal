from django.urls import path,include
from . import views

app_name = 'interview'
urlpatterns = [
    path('',views.home , name="home"),
    path('signup/',views.signup , name="signup"),
]