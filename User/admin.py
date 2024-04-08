from django.contrib import admin
from .models import Manager, Organizer, Exhibitor
# Register your models here.
admin.site.register(Manager)
admin.site.register(Organizer)
admin.site.register(Exhibitor)