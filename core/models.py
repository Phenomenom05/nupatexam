import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=300, null=True, blank=True)
    username = models.CharField(max_length=300, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    def __str__(self):
        return self.name    


class Exam(models.Model):
    name = models.CharField(max_length=300, null=True, blank=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    def __str__(self):
        return self.name
    



class QuestionModel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    owner = models.ForeignKey(Exam, on_delete=models.CASCADE, null=True, blank=True)
    question = models.CharField(max_length=255)
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)


def CreateProfile(sender, instance, created, **Kwargs):
    if created:
        user = instance
        profile = StudentProfile.objects.create(
            user = user,
            name = user.first_name,
            username=user.username,
            email=user.email
        )



post_save.connect(CreateProfile, sender=User)
