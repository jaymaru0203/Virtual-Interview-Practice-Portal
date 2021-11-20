from django.core.exceptions import SuspiciousFileOperation
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from datetime import datetime
import json, os

# Create your views here.
def dashboard(request):
    return redirect('/')

def instructions(request):
    return render(request, "instructions.html")

def choice(request):
    return render(request, "choice.html")

# in choice method, store the user's choice in session variable to be used further

def interview(request):
    if request.method == "POST":
        baseDir = settings.BASE_DIR
        user = request.user.email
        try:
            path = os.path.join(baseDir, "media\\interview_recordings\\")
            filename = user[0: user.index('@')] + "_" + str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) + "_" + request.POST['qs']
            # filename = str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) + "_" + request.POST['qs']
            
            # store the filename somewhere to be deleted after processing 
            
            extension = ".webm"
            with open(path + filename + extension, 'wb+') as destination:
                for chunk in request.FILES['blob'].chunks():
                    destination.write(chunk)
            return redirect('/')
            
        except:
            raise SuspiciousFileOperation 
        else:
            # No errors during processing of the uploaded recording - proceeding with updating stats for user
            messages.success(request, "Interview Completed Successfully!")
            return redirect('/')
 
    else:
        # Randomize Videos here based on user's experience level (fresher or experienced) and then assign to the list instead of hardcoding
        list = ['1.mp4', '2.mp4', '3.mp4']
        json_list = json.dumps(list)
        return render(request, "interview.html", {'videos' : json_list, 'start': "1.mp4"})

def interview_success(request):
    return render(request, "interview_success.html")
