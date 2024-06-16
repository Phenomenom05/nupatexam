from rest_framework.generics import CreateAPIView
from django.contrib.auth import authenticate, login, logout, get_user_model
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect, get_object_or_404
from rest_framework.decorators import api_view
from .models import QuestionModel, Exam, Profile, TheoryQuestion
from .serializers import SerializerQuestion, SerializerExam, SerializerCreateAccount, SerializerTheory
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse
from random import shuffle

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

@api_view(['GET'])
def GetObJQuestions(request, code):
    exam = get_object_or_404(Exam, code=code)
    questionobj = exam.questionmodel_set.all()

    question_answered_obj = request.session.get('question_answered_obj', [])
    for question in questionobj:
        if str(question.id) not in question_answered_obj:
            question_answered_obj.append(str(question.id))
            request.session['question_answered_obj'] = question_answered_obj

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
            serializer = SerializerQuestion(data=shuffled_question)  # Use data argument to pass dictionary
            if serializer.is_valid():
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    return redirect("get-theoryquestion", code=code)

@api_view(['GET'])
def GetTheoryQuestions(request, code):
    exam = get_object_or_404(Exam, code=code)
    questiontheory = exam.theoryquestion_set.all()

    # Get the list of theory questions already answered
    question_answered_theory = request.session.get('question_answered_theory', [])
    
    # Find the first unanswered question
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
        # If all questions are answered, redirect to submit
        return redirect("submit_answer_exam", code=code)
    
    return redirect("submit_answer_exam", code=code)

@api_view(['POST'])
def StartExam(request):
    if request.method == "POST":
        name_of_user = request.data.get("name")
        code = request.data.get("code")
        request.session['uniqueName'] = name_of_user
        request.session['score'] = 0
        request.session['theory_questions_answered'] = []
        return JsonResponse({"code": code, "userName": name_of_user}, status=200)


@api_view(['POST'])
def ProceedExam(request, code):
    if request.method == "POST":
        return redirect("get-objquestion", code=code)


@api_view(['POST'])
def AnswerObJQuestion(request, pk):
    if request.method == "POST":
        obj_question = get_object_or_404(QuestionModel, id=pk)
        code = obj_question.owner.code
        option_picked = request.data.get("picked")
        if option_picked == obj_question.answer:
            request.session['score'] += 1
        return redirect("get-objquestion", code=code)

@api_view(['POST'])
def AnswerTheoryQuestion(request, pk):
    if request.method == "POST":
        theory_question = get_object_or_404(TheoryQuestion, id=pk)
        code = theory_question.owner.code
        option_picked = request.data.get("picked")
        answer = {
            theory_question.question: option_picked 
        }
        request.session['theory_questions_answered'].append(answer)
        facilitator_email = theory_question.owner.owner.email

        return redirect("get-theoryquestion", code=code)

@api_view(['POST'])
def submit_answer_exam(request, code):
    score = request.session['score']
    exam = get_object_or_404(Exam, code=code)
    email = exam.owner.email
    uniqueName = request.session['uniqueName']
    theory_questions_answered = request.session['theory_questions_answered']

    subject = f"{uniqueName} has finished their exam!"
    message = f"The score is {score}. Here are the theory questions and answers: {theory_questions_answered}"
    sender_email = "phedave05@gmail.com"
    send_mail(subject, message, sender_email, [email])
    
    return Response({"detail": "Exam submitted and code sent successfully"}, status=status.HTTP_200_OK)
