from rest_framework.generics import CreateAPIView
from django.contrib.auth import authenticate, login, logout, get_user_model
from rest_framework.response import Response
from django.db import transaction, IntegrityError
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from .models import QuestionModel, Exam, Profile, TheoryQuestion
from .serializers import SerializerQuestion, SerializerExam, SerializerCreateAccount, SerializerTheory
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from random import shuffle
import uuid
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class CheckView(CreateAPIView): 
    queryset = QuestionModel.objects.all()
    serializer_class = SerializerQuestion

@login_required
@api_view(['POST'])
def CreateQuestion(request, exam_id):
    try:
        uuid_obj = uuid.UUID(exam_id, version=4)
    except ValueError:
        return JsonResponse({"detail": "Invalid UUID format"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        exam = Exam.objects.get(id=uuid_obj)
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
        uuid_obj = uuid.UUID(exam_id, version=4)
    except ValueError:
        return JsonResponse({"detail": "Invalid UUID format"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        exam = Exam.objects.get(id=uuid_obj)
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
    send_mail(subject, message, sender_email, [user_email], fail_silently=False)
    
    return JsonResponse({"detail": "Exam submitted and code sent successfully"}, status=200)

@api_view(['POST'])
def CreateAccount(request):
    if request.method == "POST":
        serializer = SerializerCreateAccount(data=request.data)
        if serializer.is_valid():
            try:
                 with transaction.atomic():
                    user = serializer.save()
                    profile = Profile.objects.create(user=user)
                    logger.info(f"User created: {user.username} (ID: {user.id})")
                    logger.info(f"Profile created for {user.username}")
                    transaction.commit()
                    return Response({"detail": "User created successfully"}, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                logger.error(f"IntegrityError creating user or profile: {str(e)}")
                transaction.rollback()
                return Response({"detail": "Error creating user or profile"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                logger.exception(f"Unexpected error creating user or profile: {str(e)}")
                transaction.rollback()
                return Response({"detail": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.error(f"Serializer errors: {serializer.errors}")
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

userDict = {}

@api_view(['GET'])
def GetObJQuestions(request, code, userName):
    exam = get_object_or_404(Exam, code=code)
    questionobj = exam.questionmodel_set.all()
    if userName not in userDict:
        userDict[userName] = {'objList': [], 'theoryList': [], 'theoryAnsweredList': [], "name": userName, 'score': []}
    objList = userDict[userName]['objList']

    for question in questionobj:
        if str(question.id) not in objList:
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
            objList.append(str(question.id))
            if serializer.is_valid():
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'detail': 'No more objective questions'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def GetTheoryQuestions(request, code, userName):
    exam = get_object_or_404(Exam, code=code)
    questiontheory = exam.theoryquestion_set.all()
    if userName not in userDict:
        userDict[userName] = {'objList': [], 'theoryList': [], 'theoryAnsweredList': [], "name": userName, 'score': []}
    theoryList =  userDict[userName]['theoryList']

    next_question = None
    for question in questiontheory:
         if str(question.id) not in theoryList:
            next_question = question
            theoryList.append(str(question.id))
            break

    if next_question:
        serializer = SerializerTheory(instance=next_question)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "All questions answered"}, status=status.HTTP_200_OK)

@api_view(['POST'])
def StartExam(request):
    userName = request.data.get("userName")
    code = request.data.get("code")
    if userName not in userDict:
        addUser = {
            userName:{
                'objList': [],
                'theoryList': [],
                'theoryAnsweredList': [],
                "name": userName,
                'score': []
            }
        }
        userDict.update(addUser)
    return JsonResponse({"code": code, "userName": userName}, status=200)

@api_view(['POST'])
def ProceedExam(request, code, userName):
    return redirect("get-objquestion", code=code, userName=userName)


@api_view(['POST'])
def AnswerObJQuestion(request, pk, userName):
    if userName not in userDict:
        return JsonResponse({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    score = userDict[userName]['score']
    try:
        uuid_obj = uuid.UUID(pk, version=4)
    except ValueError:
        return JsonResponse({"detail": "Invalid UUID format"}, status=status.HTTP_400_BAD_REQUEST)

    obj_question = get_object_or_404(QuestionModel, id=uuid_obj)
    code = obj_question.owner.code
    option_picked = request.data.get("picked")

    if option_picked == obj_question.answer:
        score.append("correct")
                
    return redirect("get-objquestion", code=code, userName=userName)

@api_view(['POST'])
def AnswerTheoryQuestion(request, pk, userName):
    if userName not in userDict:
        return JsonResponse({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    theoryAnsweredList = userDict[userName]['theoryAnsweredList']
    try:
        theory_question = get_object_or_404(TheoryQuestion, id=pk)
        code = theory_question.owner.code
        option_picked = request.data.get("picked")
        answer = {
            theory_question.question: option_picked 
        }
        
        theoryAnsweredList.append(answer)
        return redirect("get-theoryquestion", code=code, userName=userName)
    except Exception as e:
        return JsonResponse({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def submit_answer_exam(request, code, userName):
    if userName not in userDict:
        return JsonResponse({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    theoryAnsweredList = userDict[userName]['theoryAnsweredList']
    score = userDict[userName]['score']
    exam = get_object_or_404(Exam, code=code)
    email = exam.owner.email
    uniqueName = userDict[userName]['name']
    subject = f"{uniqueName} has finished their exam!"
    message = f"The score is {len(score)}. Here are the theory questions and answers: {theoryAnsweredList}"
    sender_email = "phedave05@gmail.com"
    send_mail(subject, message, sender_email, [email], fail_silently=False)

    return Response({"detail": "Exam submitted and code sent successfully"}, status=status.HTTP_200_OK)
