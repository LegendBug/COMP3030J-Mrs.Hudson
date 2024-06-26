from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone


class Manager(models.Model):
    detail = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='manager')
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


class Message(models.Model):
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    # sender/recipient : Manager/Organizer/Exhibitor, Django泛型
    # 注意这里的settings不是settings.py，而是django.conf.settings
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    is_public = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)


class MessageDetail(models.Model):
    content = models.TextField()
    message = models.ForeignKey("Message", on_delete=models.CASCADE, related_name='related_detail')
    # 设置泛型关系
    application_object_id = models.PositiveIntegerField(null=True, blank=True)
    application_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True,
                                                 blank=True, )  # limit_choices_to={'model__in': 'exhibition_application'}
    application = GenericForeignKey('application_content_type', 'application_object_id')


# 抽象申请类，数据库中不会生成对应的表
class Application(models.Model):
    class Meta:
        abstract = True

    class Stage(models.TextChoices):
        INITIAL_SUBMISSION = 'IS', 'INITIAL_SUBMISSION'  # 初始提交
        REJECTED = 'RJ', 'REJECTED'  # 拒绝申请
        ACCEPTED = 'AC', 'ACCEPTED'  # 完成申请
        CANCELLED = 'CA', 'CANCELLED'  # 取消申请

    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    description = models.TextField(default='')
    stage = models.CharField(max_length=2, choices=Stage.choices, default=Stage.INITIAL_SUBMISSION)


class GlobalSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.key}: {self.value}"
