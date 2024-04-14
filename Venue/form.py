from django import forms
from django.core.validators import MinValueValidator
from django.contrib.contenttypes.models import ContentType
from Layout.models import SpaceUnit
from .models import Venue


class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['name', 'address', 'description', 'floor', 'area', 'sectors', 'image']
        widgets = {
            'floor': forms.NumberInput(attrs={'min': 1}),
            'area': forms.NumberInput(attrs={'min': 0.01}),
        }

    def __init__(self, *args, **kwargs):
        super(VenueForm, self).__init__(*args, **kwargs)
        self.fields['floor'].validators.append(MinValueValidator(1))
        self.fields['area'].validators.append(MinValueValidator(0.01))
        self.fields['image'].required = True

    def save(self, commit=True):
        # 首先，保存Venue实例
        venue = super(VenueForm, self).save(commit=False)

        if commit:
            venue.save()  # Venue实例必须先保存以获得pk

            # Venue保存后，根据楼层数创建SpaceUnit实例
            for floor_number in range(1, venue.floor + 1):
                SpaceUnit.objects.create(
                    name=f"Venue {VenueForm.name}'s {floor_number}th Floor Layer",
                    floor=floor_number,
                    creator_content_type=ContentType.objects.get_for_model(venue),
                    creator_object_id=venue.pk
                )
        return venue
