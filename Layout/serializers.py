from rest_framework import serializers

from Statistic.models import Monitor
from .models import SpaceUnit, KonvaElement


class KonvaElementSerializer(serializers.ModelSerializer):
    layer = serializers.PrimaryKeyRelatedField(read_only=True)  # 使用SpaceUnit的序列化器来展示详细信息
    image = serializers.ImageField(use_url=True, required=False, allow_null=True)  # 确保使用URL来展示图片

    class Meta:
        model = KonvaElement
        fields = ['id', 'name', 'layer', 'type', 'data', 'transformable', 'image']
        depth = 1  # 同样适用depth以便显示更详细的关联信息
        extra_kwargs = {
            'id': {'read_only': False, 'required': True},  # 确保ID是必须的，用于更新
        }


class MonitorSerializer(serializers.ModelSerializer):
    layer = serializers.PrimaryKeyRelatedField(read_only=True)
    image = serializers.ImageField(use_url=True, required=False, allow_null=True)

    class Meta:
        model = Monitor
        fields = ['id', 'name', 'is_online', 'venue', 'layer', 'data', 'transformable', 'image']
        depth = 1
        extra_kwargs = {
            'id': {'read_only': False, 'required': True},
        }


class RecursiveSerializer(serializers.Serializer):
    """用于递归序列化的通用序列化器。"""

    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class ParentSpaceUnitSerializer(serializers.ModelSerializer):
    # 使用自身递归序列化parent_unit的parent_unit
    parent_unit = serializers.SerializerMethodField()

    def get_parent_unit(self, obj):
        if obj.parent_unit:
            return ParentSpaceUnitSerializer(obj.parent_unit, context=self.context).data
        else:
            return None

    class Meta:
        model = SpaceUnit
        fields = ['id', 'name', 'description', 'floor', 'parent_unit']


class SpaceUnitSerializer(serializers.ModelSerializer):
    child_units = RecursiveSerializer(many=True, read_only=False)
    elements = KonvaElementSerializer(many=True, read_only=False)
    monitors = MonitorSerializer(many=True, read_only=False)
    parent_unit = ParentSpaceUnitSerializer(read_only=True)

    class Meta:
        model = SpaceUnit
        fields = ['id', 'name', 'description', 'floor', 'parent_unit', 'available', 'created_at', 'child_units',
                  'elements', 'monitors', 'affiliation_content_type', 'affiliation_object_id']
        extra_kwargs = {
            'id': {'read_only': False, 'required': True},  # 确保ID是必须的，用于更新
        }
