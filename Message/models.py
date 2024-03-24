from django.db import models
from django.utils import timezone

class Message(models.Model):
    title = models.CharField(max_length=255)
    sender = models.ForeignKey('User.User', on_delete=models.CASCADE, related_name='sent_messages', null=True, blank=True)
    receiver = models.ManyToManyField('User.User', related_name='received_messages', blank=True)
    content = models.TextField()
    detail = models.OneToOneField('Message.MessageDetail', on_delete=models.CASCADE, related_name='message')
    created_at = models.DateTimeField(default=timezone.now)

class MessageDetail(models.Model):
    NOTIFICATION = 'notification'
    RESOURCE_APPLICATION = 'resource_application'
    EXTENSION_APPLICATION = 'extension_application'
    BREAKAGE_ALERT = 'breakage_alert'
    TYPE_CHOICES = [
        (NOTIFICATION, 'Notification'),
        (RESOURCE_APPLICATION, 'ResourceApplication'),
        (EXTENSION_APPLICATION, 'ExtensionApplication'),
        (BREAKAGE_ALERT, 'BreakageAlert'),
    ]
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default=NOTIFICATION)
    item = models.ForeignKey('Inventory.Item', on_delete=models.CASCADE, null=True, blank=True)
    postponed_date = models.DateTimeField(null=True, blank=True)
    resource_type = models.ForeignKey('Inventory.ResourceType', on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    is_public = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    # message = Message 反向查询

