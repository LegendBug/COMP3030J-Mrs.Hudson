import os
import uuid

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class InventoryCategory(models.Model):
    def inventory_category_upload_to(instance, filename):  # 即使不使用filename参数,也必须保留, 这是Django的硬性要求
        # 获取文件的扩展名
        extension = filename.split('.')[-1]
        # 文件将上传到 data/InventoryCategory/<模型的主键值>/filename.文件后缀
        return 'InventoryCategory/{0}/{1}.{2}'.format(instance.pk, filename, extension)

    def save(self, *args, **kwargs):
        # 如果是新对象且图片已提供，先保存对象获取pk
        if self.pk is None and self.image:
            super(InventoryCategory, self).save(*args, **kwargs)
        # 删除原有图片
        if self.image:
            # 构建目录路径
            folder_path = 'data/InventoryCategory/{0}'.format(self.pk)
            full_folder_path = os.path.join(settings.MEDIA_ROOT, folder_path)
            # 如果目录存在并且里面有文件，则清空该目录
            if default_storage.exists(full_folder_path):
                for the_file in default_storage.listdir(full_folder_path)[1]:  # 获取文件列表
                    file_path = os.path.join(full_folder_path, the_file)
                    default_storage.delete(file_path)
            # 文件名使用uuid生成，避免重复
            self.image.name = '{0}.{1}'.format(uuid.uuid4(), self.image.name.split('.')[-1])
            # 保存图片
            self.image.save(self.image.name, self.image, save=False)
        # 然后再次保存对象以包括图片
        super(InventoryCategory, self).save(*args, **kwargs)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_private = models.BooleanField(default=False)
    cost = models.FloatField(blank=True, null=True)
    # items : List<Item>, 由Django ORM的反向关系实现
    image = models.ImageField(upload_to=inventory_category_upload_to, null=True, blank=True)


# Item Model
class Item(models.Model):
    name = models.CharField(max_length=255)
    is_using = models.BooleanField(default=False)
    is_damaged = models.BooleanField(default=False)
    power = models.FloatField(blank=True, null=True)
    water_consumption = models.FloatField(blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True)
    category = models.ForeignKey("Inventory.InventoryCategory", on_delete=models.CASCADE, related_name='items')
    location = models.ForeignKey("Layout.SpaceUnit", on_delete=models.SET_NULL, null=True, related_name='items')
    # affiliation : Venue/Exhibition/Booth, Django泛型
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='items')
    object_id = models.PositiveIntegerField()
    affiliation = GenericForeignKey('content_type', 'object_id')


class ResourceApplication(models.Model):
    content = models.TextField(blank=True, null=True)
    category = models.ForeignKey("Inventory.InventoryCategory", on_delete=models.CASCADE, related_name='applications')
    quantity = models.IntegerField()
    is_approved = models.BooleanField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # sent_from : Exhibition/Booth, Django泛型
    sent_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='resource_applications')
    sent_object_id = models.PositiveIntegerField()
    sent_from = GenericForeignKey('sent_content_type', 'sent_object_id')
    # sent_to : Exhibition/Venue, Django泛型
    received_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                              related_name='unresolved_resource_applications')
    received_object_id = models.PositiveIntegerField()
    sent_to = GenericForeignKey('received_content_type', 'received_object_id')


class BreakageAlert(models.Model):
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    item = models.ForeignKey("Inventory.Item", on_delete=models.CASCADE)
    sent_to = models.ForeignKey("Venue.Venue", on_delete=models.CASCADE, related_name='breakage_alerts')
    # sent_from : Exhibition/Booth, Django泛型
    sent_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    sent_object_id = models.PositiveIntegerField()
    sent_from = GenericForeignKey('sent_content_type', 'sent_object_id')
