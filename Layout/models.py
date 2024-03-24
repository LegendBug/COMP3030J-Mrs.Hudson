from django.db import models

# SpaceType Model
class SpaceType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    # rooms = List<SpaceUnit>

# SpaceUnit Model
class SpaceUnit(models.Model):
    name = models.CharField(max_length=255)
    floor = models.IntegerField()
    type = models.ForeignKey("Layout.SpaceType", on_delete=models.CASCADE, related_name='rooms')
    # items = List<Item>
    # staffs = List<User>