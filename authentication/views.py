from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .models import User
from django.contrib import messages
from django.contrib.auth.hashers import make_password
import re

def dashboard(request):
    if request.user.is_authenticated:
        return render(request, "dashboard.html")
    else:
        return render(request, "index.html")

def signup(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        name = name.strip()
        # pattern = re.compile("/^[a-zA-Z ]*$/")
        
        # print("below")
        # print(name) 
        # print(bool(re.match(r"[a-zA-Z ]", name)))
        # print(bool(re.match(r'[\w.@+\- ]+$', name)))
        # print(bool(re.match(r"/^[a-zA-Z ]*$/", name)))
        # print(bool(re.match(r"^[\\p{L} .'-]+$", name)))
        # print(bool(re.match(r"/^[a-z ,.'-]+$/i", name)))
        # print(pattern.match(name))
        
        if len(name) == 0 or len(email) == 0 or len(password) == 0:
            messages.error(request, "Fields Marked with '*' Cannot be Empty!")
            return redirect('/signup/')
        if len(password) < 8:
            messages.error(request, "Password must contain atleast 8 characters!")
            return redirect('/signup/')
        if not re.match("^([a-zA-Z]{2,}\s[a-zA-Z]{2,}$)|([a-zA-Z]{1,}$)|([a-zA-Z]{2,}\s[a-zA-Z]{2,}\s[a-zA-Z]{2,}$)", name):
            messages.error(request, "Name must contain only Alphabets and Spaces!")
            return redirect('/signup/')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email ID Already Exists!")
            return redirect('/signup/')
        else:
            user = User.objects.create_user(email, name = name, password = password)
            user.save()
            auth_login(request, user)
            messages.success(request, "Registered Successfully!")
            return redirect('/')

    else: 
        return render(request, "signup.html")



def login(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        if len(email) == 0 or len(password) == 0:
            messages.error(request, "Fields Marked with '*' Cannot be Empty!")
            return redirect('/login/')

        user = authenticate(email = email, password = password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, "Logged In Successfully!")
            return redirect('/')
        else:
            messages.error(request, "Invalid Credentials!")
            return redirect('/login/')

    else:
        return render(request, "login.html")



def logout(request):
    auth_logout(request)
    messages.success(request, "Logged out Successfully!")
    return redirect('/')

def profile(request):
    if request.method == 'POST':
        Name = request.POST['Name']
        Email = request.POST['Email']
        Password = request.POST['Password']

        if request.user.name != Name and bool(re.match(r"[a-zA-Z]+", Name)) == False:
            messages.error(request, "Name must start with Alphabet!")
            return redirect('/profile/')
        if request.user.email != Email and User.objects.filter(email=Email).exists():
            messages.error(request, "Email ID Already Exists!")
            return redirect('/profile/')
        if(request.user.password != Password):
            if len(Password) < 8:
                messages.error(request, "Password must contain atleast 8 characters!")
                return redirect('/profile/')
            else:
                Password = make_password(Password)
        
        User.objects.filter(email=request.user.email).update(name=Name,email=Email, password=Password)
        User.objects.filter(email=request.user.email).update(name=Name,password=Password,email=Email)
        user = User.objects.get(email=Email)
        auth_login(request, user)
        info = User.objects.get(name=request.user.name)
        context = {}
        context['info'] = info
        return render(request, 'profile.html', context)

    else:
        info = User.objects.get(email=request.user.email)
        context = {}
        context['info'] = info
        return render(request, 'profile.html', context)
