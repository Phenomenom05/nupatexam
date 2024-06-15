from django.urls import path
from .views import * 

urlpatterns = [
    path('', CheckView.as_view(), name="home"),
    path("create-question/<str:exam_id>/", CreateQuestion, name="create-question"),
    path("create-theoryquestion/<str:exam_id>/", CreateTheory, name="create-theoryquestion"),
    path("create-exam/", CreateExam, name="create-exam"),
    path("create-account/", CreateAccount, name="create-account"),
    path("signin/", Signin, name="signin"),
    path("signout/", Signout,name="signout"),
    path("get-objquestion/<str:code>", GetObJQuestions, name="get-objquestion"),
    path("get-theoryquestion/<str:code>", GetTheoryQuestions, name="get-theoryquestion"),
    path("start-exam", StartExam, name="start-exam"),
    path("answer-objquestion/<str:pk>", AnswerObJQuestion, name="answer-objquestion"),
    path("answer-theoryquestion/<str:pk>", AnswerTheoryQuestion, name="answer-theoryquestion"),
    path("submit-exam/<str:exam_id>/", submit_exam, name="submit-exam"),
    path("submit-answer-exam/<str:pk>/", submit_answer_exam, name="submit_answer_exam"),


]
