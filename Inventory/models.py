from django.db import models

# ResourceType Model
class ResourceType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    # items : List<Item>

# Item Model
class Item(models.Model):
    name = models.CharField(max_length=255)
    is_using = models.BooleanField(default=False)
    is_damaged = models.BooleanField(default=False)
    cost = models.FloatField()
    power = models.FloatField()
    water_consumption = models.FloatField()
    usage_start = models.TimeField(null=True, blank=True)  # 一天内的使用开始时间
    usage_end = models.TimeField(null=True, blank=True)  # 一天内的使用结束时间
    return_date = models.DateTimeField()
    last_modified = models.DateTimeField(auto_now=True)
    type = models.ForeignKey("Inventory.ResourceType", on_delete=models.CASCADE, related_name='items')
    owner = models.ForeignKey("User.User", on_delete=models.SET_NULL, null=True, related_name='items')
    location = models.ForeignKey("Layout.SpaceUnit", on_delete=models.SET_NULL, null=True, related_name='items')
