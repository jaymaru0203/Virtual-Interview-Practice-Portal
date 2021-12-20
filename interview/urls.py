from django.urls import path,include
from . import views

app_name = 'interview'
urlpatterns = [
    path('' ,views.dashboard, name='dashboard'),    
    path('instructions/<str:choice>/' ,views.instructions, name='instructions'),    
    path('choice/' ,views.choice, name='choice'),    
    path('interview/' ,views.interview, name='interview'),   
    path('resources/' ,views.resources, name='interview_success'),   
    path('technical/' ,views.technical, name='technical'),  
    path('interview_success/' ,views.interview_success, name='interview_success'),    
]

