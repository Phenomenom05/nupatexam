from rest_framework.generics import CreateAPIView
from django.contrib.auth import authenticate, login, logout, get_user_model
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from django.shortcuts import redirect, get_object_or_404, HttpResponse
from rest_framework.decorators import api_view
from .models import QuestionModel, Exam, Profile, TheoryQuestion
from .serializers import SerializerQuestion, SerializerExam, SerializerCreateAccount, SerializerTheory
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse
from random import shuffle
import uuid

User = get_user_model()

class CheckView(CreateAPIView): 
    queryset = QuestionModel.objects.all()
    serializer_class = SerializerQuestion

@login_required
@api_view(['POST'])
def CreateQuestion(request, exam_id):
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return Response({"detail": "Exam not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "POST":
        serializer = SerializerQuestion(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=exam)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
@api_view(['POST'])
def CreateTheory(request, exam_id):
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return Response({"detail": "Exam not found."}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == "POST":
        serializer = SerializerTheory(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=exam)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
@api_view(['POST'])
def CreateExam(request):
    if request.method == "POST":
        profile = request.user.profile
        serializer = SerializerExam(data=request.data)
        if serializer.is_valid():
            exam = serializer.save(owner=profile)
            return Response({"examId": str(exam.id)}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
@api_view(['POST'])
def submit_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    user_email = exam.owner.email
    name = exam.owner.name
    code = exam.code
    
    subject = f"{name}, you have successfully created your exam questions!"
    message = f"The exam code for {exam.name} is {code}. Share this code with your students so they can take the exam."
    sender_email = "phedave05@gmail.com"
    send_mail(subject, message, sender_email, [user_email])
    
    return JsonResponse({"detail": "Exam submitted and code sent successfully"}, status=200)

@api_view(['POST'])
def CreateAccount(request):
    if request.method == "POST":
        serializer = SerializerCreateAccount(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def Signin(request):
    if request.method == 'POST':
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"Details": "Login Successful"}, status=status.HTTP_200_OK)
        else:
            return Response({"Details": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    return Response({"Details": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@login_required
@api_view(['POST'])
def Signout(request):
    logout(request)
    return redirect("signin")

question_answered_obj = []
@api_view(['GET'])
def GetObJQuestions(request, code):
    exam = get_object_or_404(Exam, code=code)
    questionobj = exam.questionmodel_set.all()
 
    for question in questionobj:
        if str(question.id) not in question_answered_obj:
            options = [question.option1, question.option2, question.option3, question.answer]
            shuffle(options)
            shuffled_question = {
                'id': str(question.id),
                'question': question.question,
                'option1': options[0],
                'option2': options[1],
                'option3': options[2],
                'answer': options[3],
            }
            serializer = SerializerQuestion(data=shuffled_question)
              # Use data argument to pass dictionary
            question_answered_obj.append(str(question.id))
            if serializer.is_valid():
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
           
    
    return Response({'detail': 'No more objective questions'}, status=status.HTTP_204_NO_CONTENT)


question_answered_theory = []
@api_view(['GET'])
def GetTheoryQuestions(request, code):
    exam = get_object_or_404(Exam, code=code)
    questiontheory = exam.theoryquestion_set.all()

    # Assuming question_answered_theor is stored somewhere (session, database, etc.)
    # Ensure it's initialized and accessible across requests

    next_question = None
    for question in questiontheory:
        if str(question.id) not in question_answered_theory:
            next_question = question
            question_answered_theory.append(str(question.id))
            break

    if next_question:
        # If there's a next question, serialize it and return
        serializer = SerializerTheory(instance=next_question)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "All questions answered"}, status=status.HTTP_200_OK)




Name = []
@api_view(['POST'])
def StartExam(request):
    if request.method == "POST":
        name_of_user = request.data.get("name")
        code = request.data.get("code")
        Name.append(name_of_user)
        return JsonResponse({"code": code, "userName": name_of_user}, status=200)


@api_view(['POST'])
def ProceedExam(request, code):
    if request.method == "POST":
        return redirect("get-objquestion", code=code)

Score = []
@api_view(['POST'])
def AnswerObJQuestion(request, pk):
    if request.method == "POST":
        try:
            uuid_obj = uuid.UUID(pk, version=4)
        except ValueError:
            return HttpResponse("Invalid UUID format")
        obj_question = get_object_or_404(QuestionModel, id=uuid_obj)
        code = obj_question.owner.code
        option_picked = request.data.get("picked")
        if option_picked == obj_question.answer:
            Score.append("correct")
        return redirect("get-objquestion", code=code)

theory_questions_answered = []
@api_view(['POST'])
def AnswerTheoryQuestion(request, pk):
    if request.method == "POST":
        theory_question = get_object_or_404(TheoryQuestion, id=pk)
        code = theory_question.owner.code
        option_picked = request.data.get("picked")
        answer = {
            theory_question.question: option_picked 
        }
        theory_questions_answered.append(answer)
        facilitator_email = theory_question.owner.owner.email

        return redirect("get-theoryquestion", code=code)

@api_view(['POST'])
def submit_answer_exam(request, code):
    score = len(Score)
    exam = get_object_or_404(Exam, code=code)
    email = exam.owner.email
    uniqueName = Name[0]
    subject = f"{uniqueName} has finished their exam!"
    message = f"The score is {score}. Here are the theory questions and answers: {theory_questions_answered}"
    sender_email = "phedave05@gmail.com"
    send_mail(subject, message, sender_email, [email], fail_silently=False)
        
    return Response({"detail": "Exam submitted and code sent successfully"}, status=status.HTTP_200_OK)
    
