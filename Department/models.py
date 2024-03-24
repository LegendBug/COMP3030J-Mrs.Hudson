from django.db import models
# Department Model
class Department(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    # staffs = List<User>
    starter_kits = models.ManyToManyField('Inventory.ResourceType', through='Department.StarterKit', related_name='departments') # Department和ResourceType之间的多对多关系, 通过StarterKit中间表来实现

class StarterKit(models.Model):
    department = models.ForeignKey("Department.Department", on_delete=models.CASCADE)
    resource_type = models.ForeignKey("Inventory.ResourceType", on_delete=models.CASCADE)
    quantity = models.IntegerField()
    class Meta:
        # 确保部门和资源类型的组合是唯一的
        unique_together = ('department', 'resource_type')
