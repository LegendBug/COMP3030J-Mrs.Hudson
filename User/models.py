from django.contrib.auth.models import AbstractUser
from django.db import models


# User Model
class User(AbstractUser):
    department = models.ForeignKey('Department.Department', on_delete=models.CASCADE, null=True, blank=True, related_name='staffs')
    office_room = models.ForeignKey('Layout.SpaceUnit', on_delete=models.SET_NULL, null=True, blank=True, related_name='staffs')
    # items = List<Item>
    # sent_messages = List<Message>
    # received_messages = List<Message>
    # chats = List<Chat>
