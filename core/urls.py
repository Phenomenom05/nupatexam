from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns = [
    # JWT token endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Your existing URLs
    path('', CheckView.as_view(), name="home"),
    path("create-question/<str:exam_id>/", CreateQuestion, name="create-question"),
    path("create-theoryquestion/<str:exam_id>/", CreateTheory, name="create-theoryquestion"),
    path("create-exam/", CreateExam, name="create-exam"),
    path("create-account/", CreateAccount, name="create-account"),
    path("signin/", Signin, name="signin"),
    path("signout/", Signout, name="signout"),
    path("get-objquestion/<str:code>/<str:userName>/", GetObJQuestions, name="get-objquestion"),
    path("get-theoryquestion/<str:code>/<str:userName>/", GetTheoryQuestions, name="get-theoryquestion"),
    path("start-exam/", StartExam, name="start-exam"),
    path("answer-objquestion/<str:pk>/<str:userName>/", AnswerObJQuestion, name="answer-objquestion"),
    path("answer-theoryquestion/<str:pk>/<str:userName>/", AnswerTheoryQuestion, name="answer-theoryquestion"),
    path("submit-exam/<str:exam_id>/", submit_exam, name="submit-exam"),
    path("submit-answer-exam/<str:code>/<str:userName>/", submit_answer_exam, name="submit_answer_exam"),
    path("proceed-exam/<str:code>/<str:userName>/", ProceedExam, name="proceed-exam"),
]