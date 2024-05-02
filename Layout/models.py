import os
import uuid
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class SpaceUnit(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    floor = models.IntegerField()
    parent_unit = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, related_name='child_units')
    available = models.BooleanField(default=False)  # boolean field: available, 用于标记当前SpaceUnit是否可被预约或使用
    # elements = List<FabricElement>, 由Django ORM的反向关系实现
    # child_units = List<SpaceUnit>, 由Django ORM的反向关系实现
    # items = List<Item>, 由Django ORM的反向关系实现
    # affiliation : Venue/Exhibition/Booth, Django泛型
    affiliation_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='sectors')
    affiliation_object_id = models.PositiveIntegerField()
    affiliation = GenericForeignKey('affiliation_content_type', 'affiliation_object_id')


class FabricElement(models.Model):
    class ElementType(models.TextChoices):
        PATH = 'Path', _('Path')
        RECTANGLE = 'Rectangle', _('Rectangle')
        TRIANGLE = 'Triangle', _('Triangle')
        CIRCLE = 'Circle', _('Circle')
        LINE = 'Line', _('Line')
        ARROW = 'Arrow', _('Arrow')
        TEXT = 'Text', _('Text')
        IMAGE = 'Image', _('Image')

    def element_upload_to(instance, filename):
        # 获取文件的扩展名
        extension = filename.split('.')[-1]
        # 生成一个新的UUID文件名
        new_filename = '{0}.{1}'.format(uuid.uuid4(), extension)
        return 'Venue/{0}'.format(new_filename)

    def save(self, *args, **kwargs):
        if self.pk:  # 如果模型已经存在，则是更新过程
            old_venue = FabricElement.objects.get(pk=self.pk)
            if old_venue.image and old_venue.image != self.image:
                if os.path.isfile(old_venue.image.path):
                    os.remove(old_venue.image.path)  # 删除旧图片

        # 保存图片到新的路径
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):  # 重写了delete方法,使得删除前能够移除图片文件
        # 删除相关图片文件
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)

    name = models.CharField(max_length=255)
    layer = models.ForeignKey(SpaceUnit, on_delete=models.CASCADE,
                              related_name='elements')  # 当前Element所在的SpaceUnit(层级)
    type = models.CharField(max_length=20, choices=ElementType.choices)
    data = models.JSONField()  # FabricJS的JSON数据
    image = models.ImageField(upload_to=element_upload_to, null=True, blank=True)  # 如果是FabricJS的Image
