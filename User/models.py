from django.contrib.auth.models import AbstractUser
from django.db import models


class Manager(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # venues : List<Venue>, 由Django ORM的反向关系实现
    # notifications : List<Notification>, 由Django ORM的反向关系实现
    # chats : List<Chat>, 由Django ORM的反向关系实现


class Organizer(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # exhibitions : List<Exhibition>, 由Django ORM的反向关系实现
    # exhibition_applications : List<ExhibitionApplication>, 由Django ORM的反向关系实现
    # notifications : List<Notification>, 由Django ORM的反向关系实现
    # chats : List<Chat>, 由Django ORM的反向关系实现


class Exhibitor(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # booths : List<Booth>, 由Django ORM的反向关系实现
    # booth_applications : List<BoothApplication>, 由Django ORM的反向关系实现
    # notifications : List<Notification>, 由Django ORM的反向关系实现
    # notifications : List<Notification>, 由Django ORM的反向关系实现
    # chats : List<Chat>, 由Django ORM的反向关系实现
