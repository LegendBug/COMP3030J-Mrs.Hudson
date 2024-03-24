from django.db import models
from django.utils import timezone
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
    content = models.TextField()
    user = models.ForeignKey("User.User", on_delete=models.CASCADE, related_name='chats')
    created_at = models.DateTimeField(default=timezone.now)