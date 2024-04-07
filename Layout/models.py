from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class SpaceUnit(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    floor = models.IntegerField()
    parent_unit = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, related_name='child_units')
    # child_units = List<SpaceUnit>, 由Django ORM的反向关系实现
    # items = List<Item>, 由Django ORM的反向关系实现
    # creator : Manager/Organizer/, Django泛型
    creator_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    creator_object_id = models.PositiveIntegerField()
    creator = GenericForeignKey('creator_content_type', 'creator_object_id')
