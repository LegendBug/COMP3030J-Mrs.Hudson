from django.db import models
from django.contrib.auth.models import User
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

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_input = models.TextField()
    copilot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    item = models.ForeignKey("Inventory.Item", on_delete=models.CASCADE)
    # sent_to : Manager/Organizer/Exhibitor, Django泛型
    recipient_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='notifications')
    recipient_object_id = models.PositiveIntegerField()
    sent_to = GenericForeignKey('recipient_content_type', 'recipient_object_id')
