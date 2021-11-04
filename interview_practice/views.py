from django.shortcuts import render,redirect
from django.http import HttpResponse

def home(request):
    return render(request, "home.html")

def signup(request):
    return render(request, "signup.html")