from enum import unique
from django.db import models
from django.db.models.deletion import DO_NOTHING
from authentication.models import User
from django.core.validators import FileExtensionValidator
import os

from interview_practice_portal.settings import BASE_DIR


# Create your models here.

INTERVIEW_CHOICE = (("experienced", "Experienced"), ("fresher", "Fresher"))

QUESTION_VIDEO_CHOICE = (
    ("initial", "Initial"),
    ("intermediate", "Intermediate"),
    ("concluding", "Concluding"),
)


def create_path_and_rename(instance, old_filename):
    dir_path = os.path.join(
        BASE_DIR, "media", "questions", instance.choice, instance.section
    )
    count = 0
    # Iterate directory
    for path in os.listdir(dir_path):
        # check if current path is a file
        if os.path.isfile(os.path.join(dir_path, path)):
            count += 1
    ext = old_filename.split(".")[-1]
    filename = "{}.{}".format(count + 1, ext)
    instance.filename = filename
    upload_to = os.path.join("questions", instance.choice, instance.section)
    return os.path.join(upload_to, filename)


class Question(models.Model):
    class Meta:
        unique_together = ["choice", "section", "filename"]

    choice = models.CharField(max_length=20, choices=INTERVIEW_CHOICE)
    question = models.CharField(max_length=250)
    section = models.CharField(max_length=15, choices=QUESTION_VIDEO_CHOICE)
    video = models.FileField(
        upload_to=create_path_and_rename,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["MOV", "avi", "mp4", "webm", "mkv"]
            )
        ],
    )
    filename = models.CharField(max_length=80, null=True, blank=True)


class Interview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    interview_start_time = models.CharField(max_length=50, null=False)
    choice = models.CharField(max_length=20, choices=INTERVIEW_CHOICE)
    duration = models.IntegerField(blank=True, null=True)


class InterviewDetail(models.Model):
    interview_id = models.ForeignKey(Interview, on_delete=models.CASCADE)
    question_no = models.IntegerField()
    question = models.CharField(max_length=250)
    answer = models.TextField()
    correct_answer = models.TextField()
    analysis = models.TextField()
    stopWords_frequency = models.FloatField()
    correction_frequency = models.IntegerField()
    nature = models.TextField()
    confidence_percent = models.IntegerField()
