from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from Inventory.models import Item
from Statistic.models import Usage

@receiver(post_save, sender=Item)
def manage_item_usage(sender, instance, created, **kwargs):
    if created:
        # 当新的 Item 创建时，不需要处理 usage
        return
    else:
        # 检查 is_using 的状态变化
        previous_is_using = instance.__class__.objects.get(id=instance.id).is_using
        if instance.is_using and not previous_is_using:
            # is_using 从 False 变为 True，开始新的使用
            Usage.objects.create(
                item=instance,
                start_time=now(),
                location_content_type=instance.affiliation_content_type,
                location_object_id=instance.affiliation_object_id
            )
        elif not instance.is_using and previous_is_using:
            # is_using 从 True 变为 False，结束当前的使用
            usage = Usage.objects.filter(item=instance).latest('start_time')
            usage.end_time = now()
            duration_hours = (usage.end_time - usage.start_time).total_seconds() / 3600
            usage.water_consumption = duration_hours * instance.water_consumption if instance.water_consumption else None
            usage.power_consumption = duration_hours * instance.power if instance.power else None
            usage.save()
