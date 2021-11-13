from django.urls import path,include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'authentication'
urlpatterns = [
    path('' ,views.dashboard, name='dashboard'),
    path('signup/' ,views.signup, name='signup'),
    path('login/' ,views.login, name='login'),
    path('logout/' ,views.logout, name='logout'),

    # Use following format for custom template instead of Django's default
    # path('reset_password/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='reset_password'),

    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
]