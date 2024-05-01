import os
import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from User.models import Application


class Exhibition(models.Model):
    def exhibition_upload_to(instance, filename):  # 即使不使用filename参数,也必须保留, 这是Django的硬性要求
        # 获取文件的扩展名
        extension = filename.split('.')[-1]
        # 生成一个新的UUID文件名
        new_filename = '{0}.{1}'.format(uuid.uuid4(), extension)
        return 'Exhibition/{0}'.format(new_filename)

    def save(self, *args, **kwargs):
        if self.pk:  # 如果模型已经存在，则是更新过程
            old_venue = Exhibition.objects.get(pk=self.pk)
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
    description = models.TextField(blank=True, null=True)
    organizer = models.ForeignKey("User.Organizer", on_delete=models.CASCADE, related_name='exhibitions')
    venue = models.ForeignKey("Venue.Venue", on_delete=models.CASCADE, related_name='exhibitions')
    sectors = GenericRelation('Layout.SpaceUnit', content_type_field='affiliation_content_type',
                              object_id_field='affiliation_object_id')
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    items = GenericRelation('Inventory.Item', content_type_field='affiliation_content_type',
                            object_id_field='affiliation_object_id')  # items = List<Item>, 由Django ORM的反向关系实现
    inventory_categories = GenericRelation('Inventory.InventoryCategory',
                                           content_type_field='origin_content_type',
                                           object_id_field='origin_object_id')
    # booths : List<Booth>, 由Django ORM的反向关系实现
    # booth_applications : List<ExhibitionApplication>, 由Django ORM的反向关系实现
    # resource_applications : List<ResourceApplication>, 由Django ORM的反向关系实现
    # unresolved_resource_applications : List<ResourceApplication>, 由Django ORM的反向关系实现
    image = models.ImageField(upload_to=exhibition_upload_to, null=True, blank=True)


class ExhibitionApplication(Application):
    # 更改related_name，避免与其它application冲突
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  related_name='exhibition_applications')
    # 某个展览被删除后，申请同时被删除
    exhibition = models.OneToOneField("Exhibition", on_delete=models.CASCADE, null=True,
                                      related_name='exhibition_application')
    # 某个消息被删除后，申请不会被删除
    message_details = GenericRelation("User.MessageDetail", related_query_name='exhibition_application', null=True,
                                      content_type_field='application_content_type',
                                      object_id_field='application_object_id')
