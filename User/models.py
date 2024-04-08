from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class Manager(models.Model):
    detail = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='manager')
    # venues : List<Venue>, 由Django ORM的反向关系实现
    # notifications : List<Notification>, 由Django ORM的反向关系实现
    # chats : List<Chat>, 由Django ORM的反向关系实现


class Organizer(models.Model):
    detail = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organizer')
    # exhibitions : List<Exhibition>, 由Django ORM的反向关系实现
    # exhibition_applications : List<ExhibitionApplication>, 由Django ORM的反向关系实现
    # notifications : List<Notification>, 由Django ORM的反向关系实现
    # chats : List<Chat>, 由Django ORM的反向关系实现


class Exhibitor(models.Model):
    detail = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exhibitor')
    # booths : List<Booth>, 由Django ORM的反向关系实现
    # booth_applications : List<BoothApplication>, 由Django ORM的反向关系实现
    # notifications : List<Notification>, 由Django ORM的反向关系实现
    # notifications : List<Notification>, 由Django ORM的反向关系实现
    # chats : List<Chat>, 由Django ORM的反向关系实现
