import os
import uuid

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models


class Booth(models.Model):
    def booth_upload_to(instance, filename):  # 即使不使用filename参数,也必须保留, 这是Django的硬性要求
        # 获取文件的扩展名
        extension = filename.split('.')[-1]
        # 生成一个新的UUID文件名
        new_filename = '{0}.{1}'.format(uuid.uuid4(), extension)
        return 'Booth/{0}'.format(new_filename)

    def save(self, *args, **kwargs):
        if self.pk:  # 如果模型已经存在，则是更新过程
            old_venue = Booth.objects.get(pk=self.pk)
            if old_venue.image and old_venue.image != self.image:
                if os.path.isfile(old_venue.image.path):
                    os.remove(old_venue.image.path)  # 删除旧图片
        # 保存图片到新的路径
        super().save(*args, **kwargs)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    exhibitor = models.ForeignKey("User.Exhibitor", on_delete=models.CASCADE, related_name='booths')
    exhibition = models.ForeignKey("Exhibition.Exhibition", on_delete=models.CASCADE, related_name='booths')
    sectors = GenericRelation('Layout.SpaceUnit', content_type_field='affiliation_content_type',
                              object_id_field='affiliation_object_id')
    start_at = models.DateField()
    end_at = models.DateField()
    items = GenericRelation('Inventory.Item', content_type_field='affiliation_content_type',
                            object_id_field='affiliation_object_id')  # items = List<Item>, 由Django ORM的反向关系实现
    inventory_categories = GenericRelation('Inventory.InventoryCategory',
                                           content_type_field='origin_content_type',
                                           object_id_field='origin_object_id')
    # resource_applications : List<ResourceApplication>, 由Django ORM的反向关系实现
    image = models.ImageField(upload_to=booth_upload_to, null=True, blank=True)


class BoothApplication(models.Model):
    content = models.TextField(blank=True, null=True)
    exhibitor = models.ForeignKey("User.Exhibitor", on_delete=models.CASCADE, related_name='booth_applications')
    exhibition = models.ForeignKey("Exhibition.Exhibition", on_delete=models.CASCADE, related_name='booth_applications')
    sectors = models.ForeignKey("Layout.SpaceUnit", on_delete=models.CASCADE)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    is_approved = models.BooleanField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
