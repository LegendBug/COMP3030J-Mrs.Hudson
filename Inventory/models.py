import os
import uuid
from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from User.models import Application


class InventoryCategory(models.Model):
    def inventory_category_upload_to(instance, filename):  # 即使不使用filename参数,也必须保留, 这是Django的硬性要求
        # 获取文件的扩展名
        extension = filename.split('.')[-1]
        # 生成一个新的UUID文件名
        new_filename = '{0}.{1}'.format(uuid.uuid4(), extension)
        return 'InventoryCategory/{0}'.format(new_filename)

    def save(self, *args, **kwargs):
        if self.pk:  # 如果模型已经存在，则是更新过程
            old_venue = InventoryCategory.objects.get(pk=self.pk)
            if old_venue.image and old_venue.image != self.image:
                if os.path.isfile(old_venue.image.path):
                    os.remove(old_venue.image.path)  # 删除旧图片
        # 保存图片到新的路径
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs): # 重写了delete方法,使得删除前能够移除图片文件
        # 删除相关图片文件
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=True) # 是否公开(即,是否可以被下一级的Exhibition/Booth申请)
    cost = models.FloatField(blank=True, null=True)
    # items : List<Item>, 由Django ORM的反向关系实现
    image = models.ImageField(upload_to=inventory_category_upload_to, null=True, blank=True)
    # origin, Django泛型, 表示该Category是在哪个Venue/Exhibition/Booth中被创建的
    origin_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='inventory_categories')
    origin_object_id = models.PositiveIntegerField()
    origin = GenericForeignKey('origin_content_type', 'origin_object_id')


# Item Model
class Item(models.Model):
    name = models.CharField(max_length=255)
    is_using = models.BooleanField(default=False)
    is_damaged = models.BooleanField(default=False)
    power = models.FloatField(blank=True, null=True)
    water_consumption = models.FloatField(blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True)
    category = models.ForeignKey("Inventory.InventoryCategory", on_delete=models.CASCADE, related_name='items')
    location = models.ForeignKey("Layout.SpaceUnit", on_delete=models.SET_NULL, null=True, related_name='items') # Item当前正位于哪一个SpaceUnit
    # affiliation : Venue/Exhibition/Booth, Django泛型
    affiliation_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='items')
    affiliation_object_id = models.PositiveIntegerField()
    affiliation = GenericForeignKey('affiliation_content_type', 'affiliation_object_id')


class ResourceApplication(Application):
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  related_name='resource_applications')

    content = models.TextField(blank=True, null=True)
    category = models.ForeignKey("Inventory.InventoryCategory", on_delete=models.CASCADE, related_name='applications')
    quantity = models.IntegerField()
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
