from rest_framework.generics import CreateAPIView
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from rest_framework.decorators import api_view
from .models import QuestionModel, Exam, StudentProfile
from .serializers import SerializerQuestion, SerializerExam, SerializerCreateAccount

class CheckView(CreateAPIView):
    questions = QuestionModel.objects.all()
    serializer_class = SerializerQuestion

@api_view(['POST'])  
def CreateQuestion(request, exam_id):
    print(exam_id)
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return Response({"detail": "Exam not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "POST":
        print("Hiii") 
        serializer = SerializerQuestion(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=exam)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])  
def CreateExam(request):
    if request.method == "POST":
        serializer = SerializerExam(data=request.data)
        if serializer.is_valid():
            exam = serializer.save()
        # Store exam_id in session
            return Response({"examId": str(exam.id)}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 


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
            return Response({"Details: Login Succesfull"}, status=status.HTTP_200_OK)
        else:
            return Response({"Details: Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    return Response({"Details: Method not allowed"}, status=status.HTTP_405__METHOD_NOT_ALLOWED)


def Signout(request):
    logout(user)
    return redirect("signin")

# api_view(['GET'])  
# def GetQuestions(request):
#     question_answered = []
#     questions =  QuestionModel.objects.all()
#     for question in questions:
#         if question.id not in question_answered:
#             question_answered.append(question.id)
#             options = [question.option1, question.option2, question.option3, question.answer]
#             shuffle(options)
#             shuffled_question = {
#             'id': question.id,
#             'question': question.question,
#             'option1': options[0],
#             'option2': options[1],
#             'option3': options[2],
#             'answer': options[3],  # Correct answer remains at the same index
#         }
#             serializer = SerializerQuestion(shuffled_question)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#             break


# score = 0
# api_view(['GET'])  
# def AnswerQuestion(request):
#     if request.method == "POST":
#         pk = request.data.get("id")
#         option_picked = request.data.get("picked")
#         question = QuestionModel.objects.get(id=pk)
#         if question.answer == option_picked:
#             score +=1 
        
    


