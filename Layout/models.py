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
    # affiliation : Venue/Exhibition/Booth, Django泛型
    affiliation_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='sectors')
    affiliation_object_id = models.PositiveIntegerField()
    affiliation = GenericForeignKey('affiliation_content_type', 'affiliation_object_id')
