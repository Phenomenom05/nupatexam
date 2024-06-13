from django.contrib import admin
from .models import QuestionModel, StudentProfile, Exam
# Register your models here.
admin.site.register(QuestionModel)
admin.site.register(Exam)
admin.site.register(StudentProfile)
