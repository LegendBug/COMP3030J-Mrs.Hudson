from django import forms
from django.core.validators import MinValueValidator
from django.contrib.contenttypes.models import ContentType
from Layout.models import SpaceUnit
from .models import Venue


class CreateVenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['name', 'address', 'description', 'floor', 'area', 'image']
        widgets = {
            'floor': forms.NumberInput(attrs={'min': 1}),
            'area': forms.NumberInput(attrs={'min': 0.01}),
        }

    def __init__(self, *args, **kwargs):
        super(CreateVenueForm, self).__init__(*args, **kwargs)
        self.fields['floor'].validators.append(MinValueValidator(1))
        self.fields['area'].validators.append(MinValueValidator(0.01))
        self.fields['image'].required = True

    def save(self, commit=True):
        # 首先，保存Venue实例
        venue = super(CreateVenueForm, self).save(commit=False)
        if commit:
            venue.save()  # Venue实例必须先保存以获得pk
            # 创建SpaceUnit实例并与Venue实例关联
            for floor_number in range(1, venue.floor + 1):
                SpaceUnit.objects.create(
                    name=f"{floor_number}",
                    description=f"{venue.name}'s Floor {floor_number}, this is one of the root SpaceUnits",
                    floor=floor_number,
                    parent_unit=None,  # 假设这是顶级单位
                    affiliation_content_type=ContentType.objects.get_for_model(Venue),
                    affiliation_object_id=venue.pk,
                )
                # 注意：这里我们不需要手动添加SpaceUnit到Venue的sectors，因为GenericRelation会自动处理反向关系
        return venue