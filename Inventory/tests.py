from unittest import TestCase
from django.contrib.contenttypes.models import ContentType
from Inventory.models import Item
from Statistic.models import Usage
from Venue.models import Venue


class TestItemSignalHandlers(TestCase):
    def setUp(self):
        #创建一个Item实例
        self.item = Item.objects.create(
            name='test_item',
            water_consumption=10,
            power=20,
            category_id=1,
            affiliation_content_type=ContentType.objects.get_for_model(Venue),
            affiliation_object_id=1
        )
        #创建一个Usage实例
        self.usage = Usage.objects.create(
            item=self.item,
            location_content_type=self.item.affiliation_content_type,
            location_object_id=self.item.affiliation_object_id
        )

    def test_manage_item_usage(self):
        # 测试is_using从False变为True的情况
        self.item.is_using = True
        #manage_item_usage(sender=Item, instance=self.item, created=False)
        # 检查是否创建了新的Usage实例
        self.assertTrue(Usage.objects.filter(item=self.item).exists())

        # 测试is_using从True变为False的情况
        self.item.is_using = False
        #manage_item_usage(sender=Item, instance=self.item, created=False)
        # 检查是否更新了Usage实例的end_time和consumption
        usage_queryset = Usage.objects.filter(item=self.item)
        self.assertTrue(usage_queryset.exists())
        usage = usage_queryset.first()  # 获取第一个匹配的Usage实例
        self.assertIsNotNone(usage.end_time)
        self.assertIsNotNone(usage.water_consumption)
        self.assertIsNotNone(usage.power_consumption)
