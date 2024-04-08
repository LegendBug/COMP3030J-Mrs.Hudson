from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class Manager(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='managers')
    # username = models.CharField(max_length=50, unique=True)
    # password = models.CharField(max_length=50)
    # email = models.EmailField(max_length=50, unique=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    # venues : List<Venue>, 由Django ORM的反向关系实现
    # notifications : List<Notification>, 由Django ORM的反向关系实现
    # chats : List<Chat>, 由Django ORM的反向关系实现


class Organizer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organizers')
    # username = models.CharField(max_length=50, unique=True)
    # password = models.CharField(max_length=50)
    # email = models.EmailField(max_length=50, unique=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    # exhibitions : List<Exhibition>, 由Django ORM的反向关系实现
    # exhibition_applications : List<ExhibitionApplication>, 由Django ORM的反向关系实现
    # notifications : List<Notification>, 由Django ORM的反向关系实现
    # chats : List<Chat>, 由Django ORM的反向关系实现


class Exhibitor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exhibitors')
    # username = models.CharField(max_length=50, unique=True)
    # password = models.CharField(max_length=50)
    # email = models.EmailField(max_length=50, unique=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    # booths : List<Booth>, 由Django ORM的反向关系实现
    # booth_applications : List<BoothApplication>, 由Django ORM的反向关系实现
    # notifications : List<Notification>, 由Django ORM的反向关系实现
    # notifications : List<Notification>, 由Django ORM的反向关系实现
    # chats : List<Chat>, 由Django ORM的反向关系实现
