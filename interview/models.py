from enum import unique
from django.db import models


# Create your models here.

class Question(models.Model):
    class Meta:
        unique_together = ['choice', 'filename']
    INTERVIEW_CHOICE = (('experienced','Experienced'),('fresher','Fresher'))
    choice = models.CharField(max_length=80,choices = INTERVIEW_CHOICE)
    filename = models.CharField(max_length=12)
    question = models.CharField(max_length=250)