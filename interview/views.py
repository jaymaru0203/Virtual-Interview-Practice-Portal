from django.core.exceptions import SuspiciousFileOperation
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

# import en_core_web_sm
# import spacy
# from spacy.lang.en.examples import sentences
# import os
# from pocketsphinx import AudioFile, get_model_path, get_data_path

# from ibm_watson import SpeechToTextV1
# from ibm_watson.websocket import RecognizeCallback, AudioSource
# from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
# from punctuator import Punctuator
import requests
import cloudscraper
from textblob import TextBlob

# end

URL = "https://services.gingersoftware.com/Ginger/correct/jsonSecured/GingerTheTextFull"  # noqa
API_KEY = "6ae0c3a0-afdc-4532-a810-82ded0054236"


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


# def aa(request):
#     corrections = [{'start': 21, 'text': 'KJ Somaiya College', 'correct': 'the KJ Somaiya College', 'definition': None}, {'start': 16, 'text': 'from', 'correct': '', 'definition': None}]
#     eid = Interview.objects.filter(id=186).first()
#     answers = InterviewDetail.objects.filter(interview_id=eid).order_by('question_no')
#     # answers = InterviewDetail.objects.filter(question_no=6).order_by('question_no')
#     link = "https://www.ibm.com/docs/en/zos-basic-skills?topic=zos-what-is-database-management-system"
#     return render(request, "aa.html", {"link": link})


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

            # filename = user[0: user.index('@')] + "_" + request.session["interview_id"] + "_" + request.POST['qs']
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
            result = r.recognize_google(audio_file)

            # if result == "":
            #     result = "You Did Not Answer This Question"

            print("Result " + result)

            # adding punctuations
            # data = {"text": result}
            # url = "http://bark.phon.ioc.ee/punctuator"
            # response = requests.post(url, data)
            # print("PUNCTT  ", response.text)
            # punct_result = response.text

            # p = Punctuator("")
            # print("PUnchhhh   " + Punctuator.punctuate("I love dance I love some text"))

            # correcting grammar

            # commenting from here

            # parser = GingerIt()
            # print("GTRKGRT")
            # text = 'The smelt of fliwers bring back memories.'
            # correct_result  = parser.parse(text)
            correct_result = GingerIt().parse(result)
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
            if request.POST["qs"] == "1" and word in result:
                analysis += "Try asking atleast 1 or 2 questions to the interviewer. "

            print("analysis 3 " + analysis)

            if stopWords_freq > 30.0:
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
            # interview_answer.answer = str(punct_result)
            interview_answer.answer = str(result)
            interview_answer.correct_answer = str(correct_result["result"])
            interview_answer.analysis = str(analysis)
            interview_answer.stopWords_frequency = int(stopWords_freq)
            interview_answer.correction_frequency = int(cfreq)
            interview_answer.nature = str(nature_polarity)
            interview_answer.save()

            # exporting the result
            # pathw = os.path.join(baseDir, "interview_data\\interview_answers\\")
            # extensionw = ".txt"
            # with open(pathw + filename + extensionw,mode='w') as file:
            #     file.write(result)
            #     print("ready!")

            if os.path.exists(i):
                os.remove(i)
            else:
                print("The file does not exist")

            if os.path.exists(o):
                os.remove(o)
            else:
                print("The file does not exist")

            # n = nltk.tokenize.punkt.PunktSentenceTokenizer()
            # n.sentences_from_text(result)
            # print(result)

            # api_key =
            # endpoint =

            # json = {
            #     "audio_url": ""
            # }

            # headers = {
            #     "authorization": api_key,
            #     "content-type": "application/json"
            # }

            # response = requests.post(endpoint, json=json, headers=headers)
            # print(response.json())

            # apikey =
            # url =

            # # Setup Service
            # authenticator = IAMAuthenticator(apikey)
            # stt = SpeechToTextV1(authenticator=authenticator)
            # stt.set_service_url(url)

            # # Perform conversion
            # # with open('converted.mp3', 'rb') as f:
            # f = "{baseDir}\interview_data\interview_audios\{filename}.wav"

            # res = stt.recognize(audio=f, content_type='audio/mp3', model='en-US_NarrowbandModel').get_result()

            # print(res)

            # synonyms = []
            # print(wordnet.synsets("good"))
            # for syn in wordnet.synsets("reading"):
            #     for l in syn.lemmas():
            #         synonyms.append(l.name())
            # print(set(synonyms))

            # n = nltk.tokenize.punkt.PunktSentenceTokenizer()
            # n.sentences_from_text(result)

            # sents = result.replace('\n', '.\n')

            # nlp = en_core_web_sm.load()
            # text = nlp(sents)

            # for sent in text.sents:
            #     sentence = sent
            #     print(sentence)

            # model_path = get_model_path()
            # data_path = get_data_path()

            # config = {
            # 'verbose': False,
            # 'audio_file': os.path.join(data_path, ''),
            # 'buffer_size': 2048,
            # 'no_search': False,
            # 'full_utt': False,
            # 'hmm': os.path.join(model_path, 'en-us'),
            # 'lm': os.path.join(model_path, 'en-us.lm.bin'),
            # 'dict': os.path.join(model_path, 'cmudict-en-us.dict')
            # }

            # audio = AudioFile(**config)
            # for phrase in audio:
            #     print("below phrase")
            #     print(phrase)

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

        # OLD CODE TO RETRIEVE RANDOM FILES FROM OLD FILE SYSTEM
        # list = ["1.mp4"]

        # vidsInDB = len(Question.objects.filter(choice=request.session["choice"]))
        # if vidsInDB < 3:
        #     messages.error(
        #         request, "Request Cannot be Processed Right Now! Please Try Again Later"
        #     )
        #     return redirect("/")
        # if request.session["choice"] == "fresher":
        #     randomlist = random.sample(range(2, vidsInDB - 1), 1)
        # else:
        #     randomlist = random.sample(range(2, vidsInDB + 2), 4)
        # randomlist.sort()

        # for i in range(0, 1):
        #     vid = str(randomlist[i]) + ".mp4"
        #     list.append(vid)

        # list.append("16.mp4")
        # list.append("0.mp4")
        # json_videos_list = json.dumps(list)

        # questions = [Question.objects.filter(filename=1).first().question]
        # question_list = Question.objects.filter(
        #     choice=request.session["choice"], filename__in=randomlist
        # ).values_list("question", flat=True)

        # for qs in question_list:
        #     questions.append(qs)

        # questions.append(Question.objects.filter(filename=16).first().question)
        # questions.append(Question.objects.filter(filename=0).first().question)
        # json_questions_list = json.dumps(questions)

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
    interview_stop_time = datetime.now()
    interviewstart = (
        Interview.objects.filter(id=request.session["interview_id"])
        .first()
        .interview_start_time
    )
    date_object = datetime.strptime(interviewstart, "%b %d, %Y - %H:%M")
    duration = (interview_stop_time - date_object).total_seconds() / 60
    date_update = Interview.objects.filter(id=request.session["interview_id"]).first()
    date_update.duration = duration
    date_update.save()
    eid = Interview.objects.filter(id=request.session["interview_id"]).first()
    answers = InterviewDetail.objects.filter(interview_id=eid).order_by("question_no")
    details = {"start": eid.interview_start_time, "duration": eid.duration}

    del request.session["interview_id"]
    del request.session["choice"]

    return render(
        request, "interview_success.html", {"answers": answers, "details": details}
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
        "-interview_start_time"
    )
    return render(request, "all_interviews.html", {"interviews": interviews})

def pagenotfound(request):
    return render(request, "pagenotfound.html")

def full_report(request,n):
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
        answers = InterviewDetail.objects.filter(interview_id=eid).order_by("question_no")
        details = {"start": eid.interview_start_time, "duration": eid.duration}
        return render(request, "full_report.html", {"answers": answers,"details": details})
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
