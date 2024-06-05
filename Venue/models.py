import os
import uuid
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models


class Venue(models.Model):
    def venue_upload_to(instance, filename):
        # 获取文件的扩展名
        extension = filename.split('.')[-1]
        # 生成一个新的UUID文件名
        new_filename = '{0}.{1}'.format(uuid.uuid4(), extension)
        return 'Venue/{0}'.format(new_filename)

    def save(self, *args, **kwargs):
        if self.pk:  # 如果模型已经存在，则是更新过程
            old_venue = Venue.objects.get(pk=self.pk)
            if old_venue.image and old_venue.image != self.image:
                if os.path.isfile(old_venue.image.path):
                    os.remove(old_venue.image.path)  # 删除旧图片

        # 保存图片到新的路径
        super().save(*args, **kwargs)

    def delete_image(self):
        # 删除相关图片文件
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)


    def delete(self, *args, **kwargs):  # 重写了delete方法,使得删除前能够移除图片文件
        # 删除相关图片文件
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)

    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    floor = models.IntegerField()
    area = models.FloatField(blank=True, null=True)
    sectors = GenericRelation('Layout.SpaceUnit', content_type_field='affiliation_content_type',
                              object_id_field='affiliation_object_id')
    items = GenericRelation('Inventory.Item', content_type_field='affiliation_content_type',
                            object_id_field='affiliation_object_id')
    inventory_categories = GenericRelation('Inventory.InventoryCategory',
                                           content_type_field='origin_content_type',
                                           object_id_field='origin_object_id')
    usages = GenericRelation('Statistic.Usage',
                             content_type_field='location_content_type',
                             object_id_field='location_object_id')
    # exhibitions : List<Exhibition>, 由Django ORM的反向关系实现
    # exhibition_applications : List<ExhibitionApplication>, 由Django ORM的反向关系实现
    # unresolved_resource_applications : List<ResourceApplication>, 由Django ORM的反向关系实现
    # breakage_alerts : List<BreakageAlert>, 由Django ORM的反向关系实现
    image = models.ImageField(upload_to=venue_upload_to, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
