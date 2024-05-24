from django.contrib import admin
from .models import *

admin.site.register(Manager)
admin.site.register(Organizer)
admin.site.register(Exhibitor)
admin.site.register(Message)
admin.site.register(MessageDetail)