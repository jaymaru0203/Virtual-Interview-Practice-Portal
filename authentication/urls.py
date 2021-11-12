from django.urls import path,include
from . import views

app_name = 'interview'
urlpatterns = [
    path('' ,views.dashboard, name="dashboard"),
    path('signup/' ,views.signup, name="signup"),
    path('login/' ,views.login, name="login"),
    path('logout/' ,views.logout, name="logout"),
]