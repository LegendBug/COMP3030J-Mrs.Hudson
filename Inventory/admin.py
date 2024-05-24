from django.contrib import admin
from .models import *

admin.site.register(InventoryCategory)
admin.site.register(Item)
admin.site.register(ResourceApplication)
admin.site.register(BreakageAlert)
