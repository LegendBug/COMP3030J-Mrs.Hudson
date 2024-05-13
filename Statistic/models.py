from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Usage(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    item = models.ForeignKey("Inventory.Item", on_delete=models.SET_NULL, related_name='usages', null=True)
    water_consumption = models.FloatField(blank=True, null=True)
    power_consumption = models.FloatField(blank=True, null=True)
    payment = models.FloatField(blank=True, null=True)
    location_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='usages')
    location_object_id = models.PositiveIntegerField()
    location = GenericForeignKey('location_content_type', 'location_object_id')  # Venue/Exhibition
