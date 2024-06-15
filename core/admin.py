from django.contrib import admin
from .models import QuestionModel, Profile, Exam, TheoryQuestion
# Register your models here.
admin.site.register(QuestionModel)
admin.site.register(Exam)
admin.site.register(Profile)
admin.site.register(TheoryQuestion)
