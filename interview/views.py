from django.core.exceptions import SuspiciousFileOperation
from django.db.models import Avg
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import *
from django.http import HttpResponse, request
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
from .middlewares.auth import auth_middleware
from django.utils.decorators import method_decorator

# start
# from gingerit.gingerit import GingerIt

import nltk

# from nltk.corpus import stopwords
nltk.download("stopwords")
from nltk.tokenize import word_tokenize

nltk.download("punkt")
# nltk.download()
from nltk.corpus import wordnet
from nltk.tokenize import sent_tokenize, word_tokenize


import requests
import cloudscraper
from textblob import TextBlob

import zipfile

# for video processing
import tensorflow
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from keras.models import model_from_json
import cv2
import glob
import numpy as np

# video processing ends here


# end

URL = "https://services.gingersoftware.com/Ginger/correct/jsonSecured/GingerTheTextFull"  # noqa
API_KEY = "6ae0c3a0-afdc-4532-a810-82ded0054236"
MODEL = ""


class GingerIt(object):
    def __init__(self):
        self.url = URL
        self.api_key = API_KEY
        self.api_version = "2.0"
        self.lang = "US"

    def parse(self, text, verify=True):
        session = cloudscraper.create_scraper()
        request = session.get(
            self.url,
            params={
                "lang": self.lang,
                "apiKey": self.api_key,
                "clientVersion": self.api_version,
                "text": text,
            },
            verify=verify,
        )
        data = request.json()
        return self._process_data(text, data)

    @staticmethod
    def _change_char(original_text, from_position, to_position, change_with):
        return "{}{}{}".format(
            original_text[:from_position], change_with, original_text[to_position + 1 :]
        )

    def _process_data(self, text, data):
        result = text
        corrections = []

        for suggestion in reversed(data["Corrections"]):
            start = suggestion["From"]
            end = suggestion["To"]

            if suggestion["Suggestions"]:
                suggest = suggestion["Suggestions"][0]
                result = self._change_char(result, start, end, suggest["Text"])

                corrections.append(
                    {
                        "start": start,
                        "text": text[start : end + 1],
                        "correct": suggest.get("Text", None),
                        "definition": suggest.get("Definition", None),
                    }
                )

        return {"text": text, "result": result, "corrections": corrections}


def dashboard(request):
    return redirect("/")


def instructions(request, choice):

    if not request.user.is_authenticated:
        return redirect("/")

    if "interview_id" in request.session:
        Interview.objects.filter(id=request.session["interview_id"]).delete()
        del request.session["interview_id"]
        messages.error(request, "Interview Terminated Unexpectedly!")
        return redirect("/")

    if choice == "experienced" or choice == "fresher":
        request.session["choice"] = choice

        # load json and create model
        json_file = open("model.json", "r")
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)
        # load weights into new model
        loaded_model.load_weights("model_weights_new.h5")
        print("Loaded model from disk")
        global MODEL
        MODEL = loaded_model

        return render(request, "instructions.html")
    else:
        return redirect("/choice/")


# @method_decorator(auth_middleware(request))
def choice(request):
    if not request.user.is_authenticated:
        return redirect("/")

    if "interview_id" in request.session:
        Interview.objects.filter(id=request.session["interview_id"]).delete()
        del request.session["interview_id"]
        messages.error(request, "Interview Terminated Unexpectedly!")
        return redirect("/")

    return render(request, "choice.html")




def resources(request):
    return render(request, "resources.html")


def technical(request):
    return render(request, "technical.html")


def interview(request):
    if not request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        baseDir = settings.BASE_DIR
        
        user = request.user.email


        try:
            path = os.path.join(baseDir, "interview_data\\interview_recordings\\")
            filename = user[0 : user.index("@")] + "_" + request.POST["qs"]
            extension = ".webm"
            question_text = request.POST["question"]
            qs = request.POST["qs"]
            with open(path + filename + extension, "wb+") as destination:

                for chunk in request.FILES["blob"].chunks():
                    destination.write(chunk)

            i = rf"{baseDir}\interview_data\interview_recordings\{filename}.webm"
            o = rf"{baseDir}\interview_data\interview_audios\{filename}.wav"
            bitrate = 3000
            fps = 44100
            cmd = [
                get_setting("FFMPEG_BINARY"),
                "-y",
                "-i",
                i,
                "-ab",
                "%dk" % bitrate,
                "-ar",
                "%d" % fps,
                o,
            ]
            subprocess_call(cmd)
            r = speech_recognition.Recognizer()
            audio = speech_recognition.AudioFile(
                rf"{baseDir}\interview_data\interview_audios\{filename}.wav"
            )
            with audio as source:
                audio_file = r.record(source)

            try:
                result = r.recognize_google(audio_file)

                print("Result " + result)

                # adding punctuations
                data = {"text": result}
                url = "http://bark.phon.ioc.ee/punctuator"
                response = requests.post(url, data)
                print("PUNCTT  ", response.text)
                punct_result = response.text

               
                correct_result = GingerIt().parse(punct_result)
                cfreq = len(correct_result["corrections"])

                # stop words frequency
                stopWords_freq = stopWords_freq_calculator(result)

                # analysis

                analysis = ""
                for item in correct_result["corrections"]:
                    if item["definition"] == "Accept comma addition":
                        analysis += "Please take small pauses in between! "
                        break

                print("analysis 1 " + analysis)

                nature = TextBlob(result).sentiment.polarity
                print("textblob polarity " + str(nature))

                if nature <= 0.0:
                    analysis += "Your response should be more positive. "

                print("analysis 2 " + analysis)

                word = "no"
                if request.POST["qs"] == "7" and word in result:
                    analysis += (
                        "Try asking atleast 1 or 2 questions to the interviewer. "
                    )

                print("analysis 3 " + analysis)

                if stopWords_freq > 50.0:
                    s = str(stopWords_freq) + "% words in your answer are stop words. "
                    analysis += s
                    analysis += "Avoid using stop words frequently! "

                print("analysis 4 " + analysis)

                if analysis == "":
                    analysis += "Good Job! Your answer is perfect!"

                print("final analysis  " + analysis)

                if nature <= 0.0:
                    nature_polarity = "negative"
                else:
                    nature_polarity = "positive"

                print(nature_polarity)

                interview_answer = InterviewDetail()
                interview_answer.interview_id = Interview.objects.filter(
                    id=request.session["interview_id"]
                ).first()
                interview_answer.question_no = int(qs)
                interview_answer.question = str(question_text)
                interview_answer.answer = str(punct_result)
                interview_answer.correct_answer = str(correct_result["result"])
                interview_answer.analysis = str(analysis)
                interview_answer.stopWords_frequency = int(stopWords_freq)
                interview_answer.correction_frequency = int(cfreq)
                interview_answer.nature = str(nature_polarity)
                interview_answer.confidence_percent = 0
                interview_answer.save()

            except:
                interview_answer = InterviewDetail()
                interview_answer.interview_id = Interview.objects.filter(
                    id=request.session["interview_id"]
                ).first()
                interview_answer.question_no = int(qs)
                interview_answer.question = str(question_text)
                interview_answer.answer = ""
                interview_answer.correct_answer = ""
                interview_answer.analysis = ""
                interview_answer.stopWords_frequency = 0
                interview_answer.correction_frequency = 0
                interview_answer.nature = ""
                interview_answer.confidence_percent = 0
                interview_answer.save()

            

            if os.path.exists(o):
                os.remove(o)
            else:
                print("The o file does not exist")


            return HttpResponse("")

        except:
            raise SuspiciousFileOperation
        else:
            # No errors during processing of the uploaded recording - proceeding with updating stats for user
            messages.success(request, "Interview Completed Successfully!")
            return redirect("/")

    else:
        if not "choice" in request.session:
            return redirect("/")
        interview_start_time = str(datetime.now().strftime("%b %d, %Y - %H:%M"))
        interview1 = Interview()
        interview1.user = request.user
        interview1.interview_start_time = interview_start_time
        interview1.choice = request.session["choice"]
        interview1.save()
        request.session["interview_id"] = Interview.objects.latest("id").id

        list = ["introduction.mp4"]
        questions = [
            "Hello, my name is Alice and I will be your Interviewer for today. I hope you are comfortable in this environment. Why dont we start with a brief introduction of yourself."
        ]

        choice = request.session["choice"]

        dir_path = os.path.join(BASE_DIR, "media", "questions", choice)

        initial_dir = os.path.join(dir_path, "initial")
        intermediate_dir = os.path.join(dir_path, "intermediate")
        concluding_dir = os.path.join(dir_path, "concluding")

        # Generating Lists of All Questions Of Each Type for Using PYTHON.SAMPLE()
        initial_qs_list = []
        for file in os.listdir(initial_dir):
            if os.path.isfile(os.path.join(initial_dir, file)):
                initial_qs_list.append(file)

        intermediate_qs_list = []
        for file in os.listdir(intermediate_dir):
            if os.path.isfile(os.path.join(intermediate_dir, file)):
                intermediate_qs_list.append(file)

        concluding_qs_list = []
        for file in os.listdir(concluding_dir):
            if os.path.isfile(os.path.join(concluding_dir, file)):
                concluding_qs_list.append(file)

        # Selecting 2 Random Files From Initial Folder
        initial_list = random.sample(initial_qs_list, 2)
        initial_list.sort()
        for i in initial_list:
            vid = os.path.join("initial", str(i)).replace("\\", "/")
            list.append(vid)

        # getting the question text for selected files
        question_list = Question.objects.filter(
            choice=choice, section="initial", filename__in=initial_list
        ).values_list("question", flat=True)
        for qs in question_list:
            questions.append(qs)

        # Selecting 1 Random File From Intermediate Folder
        intermediate_list = random.sample(intermediate_qs_list, 1)
        intermediate_list.sort()
        for i in intermediate_list:
            vid = os.path.join("intermediate", str(i)).replace("\\", "/")
            list.append(vid)

        # getting the question text for selected files
        question_list = Question.objects.filter(
            choice=choice, section="intermediate", filename__in=intermediate_list
        ).values_list("question", flat=True)
        for qs in question_list:
            questions.append(qs)

        # Selecting 2 Random Files From Concluding Folder
        concluding_list = random.sample(concluding_qs_list, 2)
        concluding_list.sort()
        for i in concluding_list:
            vid = os.path.join("concluding", str(i)).replace("\\", "/")
            list.append(vid)

        # getting the question text for selected files
        question_list = Question.objects.filter(
            choice=choice, section="concluding", filename__in=concluding_list
        ).values_list("question", flat=True)
        for qs in question_list:
            questions.append(qs)

        list.append("last.mp4")
        questions.append(
            "Do you have any questions for us? I would be happy to answer them to your satisfaction."
        )
        list.append("final.mp4")
        questions.append(
            "Thats all from my side, thank you! You will get the results of this interview soon."
        )

        json_videos_list = json.dumps(list)
        json_questions_list = json.dumps(questions)



        return render(
            request,
            "interview.html",
            {
                "videos": json_videos_list,
                "start": list[0],
                "questions": json_questions_list,
            },
        )


def interview_success(request):

    if not request.user.is_authenticated:
        return redirect("/")
    if not "interview_id" in request.session:
        return redirect("/")

    # video processing
    baseDir = settings.BASE_DIR
    
    user = request.user.email
    video_dir = os.path.join(baseDir, "interview_data\\interview_recordings\\")
    video_images_dir = os.path.join(video_dir, "*.webm")
    path_output_dir = os.path.join(baseDir, "interview_data\\video_images\\")
    video_list = []
    for filename in glob.glob(video_images_dir):
        video_list.append(filename)

    qs = 1
    for filename in video_list:
        print("file being processed is ",filename)
        vidcap = cv2.VideoCapture(filename)
        count = 1
        li = []
        while vidcap.isOpened():
            success, im = vidcap.read()
            if success:
                gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                gray = np.array(gray, dtype="uint8")
                faceCascade = cv2.CascadeClassifier(
                    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                )
                faces = faceCascade.detectMultiScale(
                    gray, scaleFactor=1.3, minNeighbors=3, minSize=(30, 30)
                )
                if len(faces) == 1:
                    for (x, y, w, h) in faces:
                        cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        roi_color = im[y : y + h, x : x + w]
                        fname = user[0 : user.index("@")] + "_" + str(count)
                        print("fnameee ",fname)
                        cv2.imwrite(
                            os.path.join(path_output_dir, "%s.png") % fname, roi_color
                        )
                        pathw = path_output_dir + fname + ".png"
                        my_image = image.load_img(
                            pathw, target_size=(48, 48), color_mode="grayscale"
                        )
                        my_img_arr = image.img_to_array(my_image)
                        p = MODEL.predict(my_img_arr.reshape(1, 48, 48))
                        li.append(p[0][0])
                        os.remove(pathw)
                        count += 1
                else:
                    break
            else:
                break
        cv2.destroyAllWindows()
        vidcap.release()
        print("no. of images ",len(li))
        if len(li) != 0:
            confidence_percent = sum(li) / len(li)
            print("confidence percent ", confidence_percent)
            id = Interview.objects.filter(id=request.session["interview_id"]).first()
            InterviewDetail.objects.filter(interview_id=id, question_no=qs).update(
                confidence_percent=round(confidence_percent * 100)
            )
            qs += 1
        os.remove(filename)

    # video processing ends here

    interview_stop_time = datetime.now()
    interviewstart = (
        Interview.objects.filter(id=request.session["interview_id"])
        .first()
        .interview_start_time
    )
    date_object = datetime.strptime(interviewstart, "%b %d, %Y - %H:%M")
    duration = int((interview_stop_time - date_object).total_seconds() / 60)
    interview_update = Interview.objects.filter(
        id=request.session["interview_id"]
    ).first()
    interview_update.duration = duration

    answers = InterviewDetail.objects.filter(interview_id=interview_update).order_by(
        "question_no"
    )

    avg_confidence = int(
        InterviewDetail.objects.filter(interview_id=interview_update).aggregate(
            Avg("confidence_percent")
        )["confidence_percent__avg"]
    )
    avg_mistakes = int(
        InterviewDetail.objects.filter(interview_id=interview_update).aggregate(
            Avg("correction_frequency")
        )["correction_frequency__avg"]
    )
    interview_update.avg_confidence = avg_confidence
    interview_update.avg_mistakes = avg_mistakes
    interview_update.save()

    details = {
        "start": interview_update.interview_start_time,
        "duration": interview_update.duration,
        "avg_confidence": interview_update.avg_confidence,
        "avg_mistakes": interview_update.avg_mistakes,
    }
    del request.session["interview_id"]
    del request.session["choice"]

    return render(
        request,
        "full_report.html",
        {
            "answers": answers,
            "details": details,
        },
    )


def all_interviews(request):
    if not request.user.is_authenticated:
        return redirect("/")

    if "interview_id" in request.session:
        Interview.objects.filter(id=request.session["interview_id"]).delete()
        del request.session["interview_id"]
        messages.error(request, "Interview Terminated Unexpectedly!")
        return redirect("/")
    interviews = Interview.objects.filter(user=request.user).order_by(
        "interview_start_time"
    )
    return render(request, "all_interviews.html", {"interviews": interviews})


def pagenotfound(request):
    return render(request, "pagenotfound.html")


def full_report(request, n):
    if not request.user.is_authenticated:
        return redirect("/")

    if "interview_id" in request.session:
        Interview.objects.filter(id=request.session["interview_id"]).delete()
        del request.session["interview_id"]
        messages.error(request, "Interview Terminated Unexpectedly!")
        return redirect("/")

    if len(Interview.objects.filter(id=n)) == 0:
        return render(request, "pagenotfound.html")

    eid = Interview.objects.filter(id=n).first()
    if eid.user == request.user:
        answers = InterviewDetail.objects.filter(interview_id=eid).order_by(
            "question_no"
        )
        details = {
            "start": eid.interview_start_time,
            "duration": eid.duration,
            "avg_confidence": eid.avg_confidence,
            "avg_mistakes": eid.avg_mistakes,
        }
        return render(
            request, "full_report.html", {"answers": answers, "details": details}
        )
    else:
        return render(request, "pagenotfound.html")


# Extracted Functions
def stopWords_freq_calculator(result):
    word_tokens = word_tokenize(result)
    stopwords = nltk.corpus.stopwords.words("english")
    stopwords_x = [w for w in word_tokens if w in stopwords]
    stopWords_freq = len(stopwords_x) / len(word_tokens) * 100
    stopWords_freq = round(stopWords_freq, 2)
    return stopWords_freq
