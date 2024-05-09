from django.db import models


class Usage(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    item = models.ForeignKey("Inventory.Item", on_delete=models.SET_NULL, related_name='usages', null=True)
    exhibition = models.ForeignKey("Exhibition.Exhibition", on_delete=models.CASCADE, related_name='usages')
    water_consumption = models.FloatField(blank=True, null=True)
    power_consumption = models.FloatField(blank=True, null=True)
    payment = models.FloatField(blank=True, null=True)
