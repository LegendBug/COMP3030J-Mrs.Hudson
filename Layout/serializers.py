from rest_framework import serializers
from .models import SpaceUnit, KonvaElement

class KonvaElementSerializer(serializers.ModelSerializer):
    layer = serializers.PrimaryKeyRelatedField(read_only=True)  # 使用SpaceUnit的序列化器来展示详细信息
    image = serializers.ImageField(use_url=True, required=False, allow_null=True)  # 确保使用URL来展示图片

    class Meta:
        model = KonvaElement
        fields = ['id', 'name', 'layer', 'type', 'data', 'transformable','image']
        depth = 1  # 同样适用depth以便显示更详细的关联信息

class RecursiveSerializer(serializers.Serializer):
    """用于递归序列化的通用序列化器。"""
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class SpaceUnitSerializer(serializers.ModelSerializer):
    child_units = RecursiveSerializer(many=True, read_only=True)
    elements = KonvaElementSerializer(many=True, read_only=True)
    class Meta:
        model = SpaceUnit
        fields = ['id', 'name', 'description', 'floor', 'parent_unit', 'available', 'created_at', 'child_units',
                  'elements', 'affiliation_content_type', 'affiliation_object_id']
