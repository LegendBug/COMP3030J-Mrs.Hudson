from rest_framework import serializers
from .models import SpaceUnit, FabricElement


class RecursiveSerializer(serializers.Serializer):
    """用于递归序列化的通用序列化器。"""
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class SpaceUnitSerializer(serializers.ModelSerializer):
    child_units = RecursiveSerializer(many=True, read_only=True)
    elements = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = SpaceUnit
        fields = ['id', 'name', 'description', 'floor', 'parent_unit', 'available', 'created_at', 'child_units',
                  'elements', 'affiliation_content_type', 'affiliation_object_id']

class FabricElementSerializer(serializers.ModelSerializer):
    layer = SpaceUnitSerializer(read_only=True)  # 使用SpaceUnit的序列化器来展示详细信息
    image = serializers.ImageField(use_url=True)  # 确保使用URL来展示图片
    class Meta:
        model = FabricElement
        fields = ['id', 'name', 'layer', 'type', 'data', 'image']
        depth = 1  # 同样适用depth以便显示更详细的关联信息
