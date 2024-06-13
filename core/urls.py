from django.urls import path
from .views import * 

urlpatterns = [
    path('', CheckView.as_view(), name="home"),
    path("create-question/<str:exam_id>/", CreateQuestion, name="create-question"),
    path("create-exam/", CreateExam, name="create-exam"),
    path("create-account/<str:pk>", CreateAccount, name="create-account"),
    path("signin/", Signin, name="signin"),

]
