from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User


class SerializerQuestion(serializers.ModelSerializer):
    class Meta:
        model = QuestionModel
        fields = '__all__'


class SerializerExam(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ["name"]

class SerializerTheory(serializers.ModelSerializer):
    class Meta:
        model = TheoryQuestion
        fields ='__all__'



class SerializerCreateAccount(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'password1', 'password2']

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password1'])
        user.save()
        return user