from enum import unique
from django.db import models
from django.db.models.deletion import DO_NOTHING
from authentication.models import User


# Create your models here.

INTERVIEW_CHOICE = (('experienced','Experienced'),('fresher','Fresher'))

class Question(models.Model):
    class Meta:
        unique_together = ['choice', 'filename']
    choice = models.CharField(max_length=20,choices = INTERVIEW_CHOICE)
    filename = models.IntegerField()
    question = models.CharField(max_length=250)

class Interview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    interview_start_time = models.CharField(max_length=50, null=False)
    choice = models.CharField(max_length=20, choices = INTERVIEW_CHOICE)
    duration = models.IntegerField(blank=True,null=True)

class InterviewDetail(models.Model):
    interview_id = models.ForeignKey(Interview, on_delete=models.CASCADE)
    question_no = models.IntegerField()
    question = models.CharField(max_length=250)
    answer = models.TextField()
    correct_answer = models.TextField()
    analysis = models.TextField()
    frequency = models.FloatField()
    correction_frequency = models.IntegerField()
    nature = models.TextField()