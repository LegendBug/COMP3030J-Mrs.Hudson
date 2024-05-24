from django import forms
from django.core.validators import MinValueValidator
from django.contrib.contenttypes.models import ContentType
from Layout.models import SpaceUnit
from .models import Venue


class CreateVenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['name', 'description', 'address', 'area', 'floor', 'image']
        widgets = {
            'floor': forms.NumberInput(attrs={'min': 1}),
            'area': forms.NumberInput(attrs={'min': 0.01}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(CreateVenueForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Venue Name'
        self.fields['description'].label = 'Venue Description'
        self.fields['floor'].validators.append(MinValueValidator(1))
        self.fields['area'].validators.append(MinValueValidator(0.01))
        self.fields['area'].label = 'Venue Area (m*m)'
        self.fields['floor'].label = 'Number of Floors'
        self.fields['image'].required = True
        self.fields['image'].label = 'Venue Poster'

    def save(self, commit=True):
        # 首先，保存Venue实例
        venue = super(CreateVenueForm, self).save(commit=False)
        if commit:
            venue.save()  # Venue实例必须先保存以获得pk
            # 创建SpaceUnit实例并与Venue实例关联
            for floor_number in range(1, venue.floor + 1):
                SpaceUnit.objects.create(
                    name=f"Floor {floor_number} Root Layer",
                    description=f"{venue.name}'s Floor {floor_number}, this is one of the root SpaceUnits",
                    floor=floor_number,
                    available=False,
                    parent_unit=None,  # 假设这是顶级单位
                    affiliation_content_type=ContentType.objects.get_for_model(Venue),
                    affiliation_object_id=venue.pk,
                )
        return venue
