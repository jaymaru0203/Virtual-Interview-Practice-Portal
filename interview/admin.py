from django.contrib import admin
# Register your models here.
from .models import *
# Register your models to admin site, then you can add, edit, delete and search your models in Django admin site.
admin.site.register(Question)
admin.site.register(Interview)
admin.site.register(InterviewDetail)