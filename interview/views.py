from django.core.exceptions import SuspiciousFileOperation
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import *
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
        interview_start_time = str(datetime.now().strftime("%b %d, %Y - %H:%M"))
        interview1 = Interview()
        interview1.user =  request.user
        interview1.interview_start_time = interview_start_time
        interview1.choice = request.session['choice']
        interview1.save()
        request.session['interview_id'] = Interview.objects.latest('id').id

        list = ["1.mp4"]
        vidsInDB = len(Question.objects.filter(choice=request.session['choice']))
        randomlist = random.sample(range(2, vidsInDB), 5)
        randomlist.sort()

        for i in range(0,5):
            vid = str(randomlist[i])+".mp4"
            list.append(vid)

        list.append("0.mp4")
        json_videos_list = json.dumps(list)

        questions = [Question.objects.filter(choice=request.session['choice'],filename=1).first().question]
        question_list = Question.objects.filter(choice=request.session['choice'],filename__in=randomlist).values_list('question', flat=True)

        for qs in question_list:
            questions.append(qs)
        
        questions.append(Question.objects.filter(choice=request.session['choice'],filename=0).first().question)
        json_questions_list = json.dumps(questions)

        return render(request, "interview.html", {'videos' : json_videos_list, 'start': list[0], 'questions': json_questions_list})
        
        
def interview_success(request):
    interview_stop_time = str(datetime.now().strftime("%b %d, %Y - %H:%M"))
    interview_stop_time = interview_stop_time[-5:]
    interviewstart = Interview.objects.filter(id = request.session.get("interview_id")).interview_start_time
    interviewstart = interviewstart[-5:]
    interview2 = Interview()
    interview2.duration = 
    return render(request, "interview_success.html")
