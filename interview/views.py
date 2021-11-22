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

import moviepy.editor
import speech_recognition
from moviepy.video.io.VideoFileClip import *
import json, os
import speech_recognition as sr 
import moviepy.editor as mp
import sys
import subprocess as sp
import array as arr

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
            path = os.path.join(baseDir, "interview_recordings\\")
            print(baseDir)
            # filename = user[0: user.index('@')] + "_" + str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) + "_" + request.POST['qs']
            # filename = user[0: user.index('@')]
            # filename = str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) + "_" + request.POST['qs']
            filename = request.POST['qs']
            # store the filename somewhere to be deleted after processing 
            
            extension = ".webm"
            print("mediiaa1")
            with open(path + filename + extension, 'wb+') as destination:
                for chunk in request.FILES['blob'].chunks():
                    destination.write(chunk)
            print("mediiaa2" )
            

            # audio_clip = mp.AudioFileClip("F:\Django\interview_practice_portal\interview_recordings\{filename}.webm")

            # moviepy.video.io.ffmpeg_tools.ffmpeg_extract_audio("F:\Django\interview_practice_portal\interview_recordings\{filename}.webm", "F:\Django\interview_practice_portal\interview_recordings\{filename}.wav")


            # patha = os.path.join(baseDir, "media\\interview_audio\\")
            # extensiona = ".wav"
            i = rf'F:\Django\interview_practice_portal\interview_recordings\{filename}.webm'
            print("1" )
            o = rf'F:\Django\interview_practice_portal\interview_audios\{filename}.wav'
            print("2" )
            # command = 'ffmpeg -i "F:\Django\interview_practice_portal\interview_recordings\{filename}.webm" -ss 0 -to 5 "F:\Django\interview_practice_portal\interview_recordings\98.mp4"'
            bitrate=3000
            fps=44100
            digits=6
            
            cmd = [get_setting("FFMPEG_BINARY"), "-y", "-i", i, "-ab", "%dk"%bitrate,"-ar", "%d"%fps, o]
            print("5" )
            subprocess_call(cmd)
            print("4" )
            # ffm = FFMConverter()
            # stream = ffmpeg.input(rf"F:\Django\interview_practice_portal\interview_recordings\{filename}.webm")
            # print("mediiaa2" )
            # stream = ffmpeg.output(stream,rf"F:\Django\interview_practice_portal\interview_recordings\{filename}.mp4")
            # ffmpeg.run(stream)
            # ffm.solve(rf"F:\Django\interview_practice_portal\interview_recordings\{filename}.webm",rf"F:\Django\interview_practice_portal\interview_recordings\{filename}.mp4")


            print("mediiaa3")
            t="2"
            p="8"
            # myfile='F:\Django\interview_practice_portal\interview_recordings\hi.mp4'
            # print(yayyyy)
            # print(myfile)
            # Video(video=myfile).save()
            
            # video = VideoFileClip(rf"F:\Django\interview_practice_portal\media\{filename}.mp4") 
            # video.audio.write_audiofile(rf"F:\Django\interview_practice_portal\interview_recordings\{filename}.wav")
            # # video = VideoFileClip(rf"{path}\prina.mp4") 
            # # video.audio.write_audiofile(r"F:\Django\interview_practice_portal\media\interview_audio\byi.wav")
            
            
            r = speech_recognition.Recognizer()
            print(6)
            audio = speech_recognition.AudioFile(rf"F:\Django\interview_practice_portal\interview_audios\{filename}.wav")
            print(7)
            with audio as source:
                audio_file = r.record(source)
            result = r.recognize_google(audio_file)

            print(result)
            # exporting the result 
            pathw = os.path.join(baseDir, "interview_answers\\")
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
        # Randomize Videos here based on user's experience level (fresher or experienced) and then assign to the list instead of hardcoding
        list = ['1.mp4', '2.mp4', '3.mp4']
        json_list = json.dumps(list)
        return render(request, "interview.html", {'videos' : json_list, 'start': "1.mp4"})

def solve(self,i,o):
    try:
        s = ffmpeg.input(i)
        s = ffmpeg.output(s,o)
        ffmpeg.run(s)
    except:
        print("some exception")
        
def interview_success(request):
    # i = 'F:\Django\interview_practice_portal\interview_recordings\8.webm'
    # print("1" )
    # k = "1"
    # o = rf'F:\Django\interview_practice_portal\interview_recordings\{k}.wav'
    # print("2" )
    # # command = 'ffmpeg -i "F:\Django\interview_practice_portal\interview_recordings\{filename}.webm" -ss 0 -to 5 "F:\Django\interview_practice_portal\interview_recordings\98.mp4"'
    # bitrate=3000
    # fps=44100
    # digits=6
            
    # command = [get_setting("FFMPEG_BINARY"), "-y", "-i", i, "-ab", "%dk"%bitrate,"-ar", "%d"%fps, o]
    # print("5" )
    # subprocess_call(command)
    # print("4" )
    # for i in range(1,4):
    # print(i)
    # ffmpeg -i "8.webm" -crf 23 "8.mp4"
    # moviepy.video.io.ffmpeg_tools.ffmpeg_extract_subclip(filename, t1, t2, targetname=None)
    # clip = mp.VideoFileClip(rf"F:\Django\interview_practice_portal\interview_recordings\8.mpeg4") 
    # clip.audio.write_audiofile(rf"F:\Django\interview_practice_portal\interview_recordings\1.wav")
    # video = VideoFileClip() 
    # video.audio.write_audiofile(rf"F:\Django\interview_practice_portal\interview_recordings\1.wav")
    # print(i + "     " + done)
    
            
            
            
            # r = speech_recognition.Recognizer()
            # audio = speech_recognition.AudioFile(r"F:\Django\interview_practice_portal\media\interview_recordings\{filename}.wav")
            # with audio as source:
            #     audio_file = r.record(source)
            # result = r.recognize_google(audio_file)

    return render(request, "interview_success.html")
