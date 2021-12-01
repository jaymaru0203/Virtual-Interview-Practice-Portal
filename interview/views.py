from django.core.exceptions import SuspiciousFileOperation
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from datetime import datetime
import imageio
import imageio.plugins.ffmpeg
from moviepy.tools import subprocess_call
from moviepy.config import get_setting
import speech_recognition
from moviepy.video.io.VideoFileClip import *
import json, os, random


def dashboard(request):
    return redirect('/')


def instructions(request, choice):
    print(choice)
    if choice == "experienced" or choice == "fresher":
        request.session['choice'] = choice
        return render(request, "instructions.html")
    else:
        return redirect('/choice/')


def choice(request):
    return render(request, "choice.html")


def interview(request):
    if request.method == "POST":
        baseDir = settings.BASE_DIR
        user = request.user.email
        try:
            path = os.path.join(baseDir, "interview_data\\interview_recordings\\")
            print(baseDir)
            # filename = user[0: user.index('@')] + "_" + str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) + "_" + request.POST['qs']
            # filename = user[0: user.index('@')]
            # filename = str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) + "_" + request.POST['qs']
            filename = user[0: user.index('@')] + "_" + request.POST['qs']
            # store the filename somewhere to be deleted after processing 
            
            extension = ".webm"
            
            with open(path + filename + extension, 'wb+') as destination:
                for chunk in request.FILES['blob'].chunks():
                    destination.write(chunk)

            i = rf"{baseDir}\interview_data\interview_recordings\{filename}.webm"
            o = rf"{baseDir}\interview_data\interview_audios\{filename}.wav"
            bitrate=3000
            fps=44100
            cmd = [get_setting("FFMPEG_BINARY"), "-y", "-i", i, "-ab", "%dk"%bitrate,"-ar", "%d"%fps, o]
            subprocess_call(cmd)
            r = speech_recognition.Recognizer()
            audio = speech_recognition.AudioFile(rf"{baseDir}\interview_data\interview_audios\{filename}.wav")
            with audio as source:
                audio_file = r.record(source)
            result = r.recognize_google(audio_file)

            print(result)
            # exporting the result 
            pathw = os.path.join(baseDir, "interview_data\\interview_answers\\")
            extensionw = ".txt"
            with open(pathw + filename + extensionw,mode='w') as file:
                file.write(result) 
                print("ready!")
            if os.path.exists(i):
                os.remove(i)
            else:
                print("The file does not exist")

            if os.path.exists(o):
                os.remove(o)
            else:
                print("The file does not exist")
            
            return redirect('/')
            
        except:
            raise SuspiciousFileOperation 
        else:
            # No errors during processing of the uploaded recording - proceeding with updating stats for user
            messages.success(request, "Interview Completed Successfully!")
            return redirect('/')
 
    else:
        ch = request.session['choice']+"/"
        first = ch+"1.mp4"
        list = [first]

        randomlist = random.sample(range(2, 16), 5)
        randomlist.sort()

        for i in range(0,5):
            vid = ch+str(randomlist[i])+".mp4"
            list.append(vid)
    
        end = ch+"end.mp4"
        list.append(end)

        json_list = json.dumps(list)
        
        return render(request, "interview.html", {'videos' : json_list, 'start': first})
        
        
def interview_success(request):
    return render(request, "interview_success.html")
