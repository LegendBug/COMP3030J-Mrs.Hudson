import os
import uuid
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

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    organizer = models.ForeignKey("User.Organizer", on_delete=models.CASCADE, related_name='exhibitions')
    venue = models.ForeignKey("Venue.Venue", on_delete=models.CASCADE, related_name='exhibitions')
    sectors = models.ForeignKey("Layout.SpaceUnit", on_delete=models.CASCADE)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    # items = List<Item>, 由Django ORM的反向关系实现
    # booths : List<Booth>, 由Django ORM的反向关系实现
    # booth_applications : List<ExhibitionApplication>, 由Django ORM的反向关系实现
    # resource_applications : List<ResourceApplication>, 由Django ORM的反向关系实现
    # unresolved_resource_applications : List<ResourceApplication>, 由Django ORM的反向关系实现
    image = models.ImageField(upload_to=exhibition_upload_to, null=True, blank=True)


class ExhibitionApplication(Application):
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    venue = models.ForeignKey("Venue.Venue", on_delete=models.CASCADE, related_name='exhibition_applications')
    # 某个展览被删除后，申请不会被删除
    sectors = models.ManyToManyField("Layout.SpaceUnit", related_name='exhibition_applications')
    # 某个展览被删除后，申请不会被删除
    exhibition = models.OneToOneField("Exhibition", on_delete=models.SET_NULL, null=True,
                                      related_name='exhibition_application')
    # 某个消息被删除后，申请不会被删除
    message_details = GenericRelation("User.MessageDetail", related_query_name='exhibition_application')
