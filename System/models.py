from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Chat(models.Model):
    USER = 'USER'
    ASSISTANT = 'ASSISTANT'
    SYSTEM = 'SYSTEM'
    TYPE_CHOICES = [
        (USER, 'User'),
        (ASSISTANT, 'Assistant'),
        (SYSTEM, 'System'),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=USER)
    content = models.TextField(default='', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    # user : Manager/Organizer/Exhibitor, Django泛型
    user_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='chats')
    user_object_id = models.PositiveIntegerField()
    user = GenericForeignKey('user_content_type', 'user_object_id')


class Notification(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    item = models.ForeignKey("Inventory.Item", on_delete=models.CASCADE)
    # sent_to : Manager/Organizer/Exhibitor, Django泛型
    recipient_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='notifications')
    recipient_object_id = models.PositiveIntegerField()
    sent_to = GenericForeignKey('recipient_content_type', 'recipient_object_id')


class Message(models.Model):
    title = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now)
    # sender/recipient : Manager/Organizer/Exhibitor, Django泛型
    # 注意这里的settings不是settings.py，而是django.conf.settings
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    is_public = models.BooleanField(default=False)
    detail = models.OneToOneField("MessageDetail", on_delete=models.CASCADE, related_name='related_message')


class MessageDetail(models.Model):
    content = models.TextField()
    message = models.ForeignKey("Message", on_delete=models.CASCADE, related_name='related_detail')
    # 设置泛型关系
    object_id = models.PositiveIntegerField(null=True, blank=True)
    application_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True,
                                         limit_choices_to={
                                             'model__in': ('exhibition_application')})
    application = GenericForeignKey('application_type', 'object_id')


# 抽象申请类，数据库中不会生成对应的表
class Application:
    class Meta:
        abstract = True

    class Stage(models.TextChoices):
        INITIAL_SUBMISSION = 'IS', 'INITIAL_SUBMISSION'  # 初始提交
        REFINED_SUBMISSION = 'RS', 'REFINED_SUBMISSION'  # 完善提交
        REJECTED = 'RJ', 'REJECTED'  # 拒绝申请
        FINALIZED = 'FI', 'FINALIZED'  # 完成申请

    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    description = models.TextField()
    stage = models.CharField(max_length=2, choices=Stage.choices, default=Stage.INITIAL_SUBMISSION)
    # details : List<ApplicationDetail>, 由Django ORM的反向关系实现，需要在子类中定义
