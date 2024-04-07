import os
import uuid

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import models


class Exhibition(models.Model):
    def exhibition_upload_to(instance, filename): # 即使不使用filename参数,也必须保留, 这是Django的硬性要求
        # 获取文件的扩展名
        extension = filename.split('.')[-1]
        # 文件将上传到 data/Exhibition/<模型的主键值>/filename.文件后缀
        return 'Exhibition/{0}/{1}.{2}'.format(instance.pk, filename, extension)

    def save(self, *args, **kwargs):
        # 如果是新对象且图片已提供，先保存对象获取pk
        if self.pk is None and self.image:
            super(Exhibition, self).save(*args, **kwargs)
        # 删除原有图片
        if self.image:
            # 构建目录路径
            folder_path = 'data/Exhibition/{0}'.format(self.pk)
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
        super(Exhibition, self).save(*args, **kwargs)

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


class BoothApplication(models.Model):
    content = models.TextField(blank=True, null=True)
    exhibitor = models.ForeignKey("User.Exhibitor", on_delete=models.CASCADE, related_name='booth_applications')
    exhibition = models.ForeignKey("Exhibition.Exhibition", on_delete=models.CASCADE, related_name='booth_applications')
    sectors = models.ForeignKey("Layout.SpaceUnit", on_delete=models.CASCADE)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    is_approved = models.BooleanField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
