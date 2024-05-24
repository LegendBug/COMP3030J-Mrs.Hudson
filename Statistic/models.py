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


class Monitor(models.Model):
    name = models.CharField(max_length=255)
    is_online = models.BooleanField(default=True)
    venue = models.ForeignKey("Venue.Venue", on_delete=models.CASCADE, related_name='monitors')
    layer = models.ForeignKey('Layout.SpaceUnit', on_delete=models.CASCADE,
                              related_name='monitors')  # 当前Element所在的SpaceUnit(层级)
    data = models.JSONField(null=True, blank=True)  # KonvaJS的JSON数据
    transformable = models.BooleanField(default=True)  # 是否可以被拖动、缩放、旋转等操作
    image = models.ImageField(null=True, blank=True, default='Monitor/monitor.png')  # 如果是KonvaJS的Image
    # captures : List<Capture>, 由Django ORM的反向关系实现


class Capture(models.Model):
    # time = models.DateTimeField(auto_now_add=True)
    time = models.DateTimeField()
    monitor = models.ForeignKey("Statistic.Monitor", on_delete=models.CASCADE, related_name='captures')
    flow_number = models.IntegerField()
