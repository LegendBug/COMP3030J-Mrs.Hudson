from django import forms
from django.contrib.contenttypes.models import ContentType
from Booth.models import Booth
from Exhibition.models import Exhibition
from Layout.models import SpaceUnit
from Venue.models import Venue


class AddLayerForm(forms.ModelForm):
    parent_unit = forms.ModelChoiceField(queryset=SpaceUnit.objects.all(), widget=forms.HiddenInput(), required=False)
    floor = forms.IntegerField(widget=forms.HiddenInput())
    user_type = forms.CharField(widget=forms.HiddenInput())
    affiliation_object_id = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = SpaceUnit
        fields = ['name', 'description', 'available', 'parent_unit', 'floor', 'user_type', 'affiliation_object_id']

    def __init__(self, *args, **kwargs):
        super(AddLayerForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['available'].initial = False

    def save(self, commit=True):
        # 保存SpaceUnit实例
        space_unit = super(AddLayerForm, self).save(commit=False)

        parent_id = self.cleaned_data.get('parent_unit_id')
        floor = self.cleaned_data.get('floor')
        user_type = self.cleaned_data.get('user_type')
        if user_type == 'Manager':
            affiliation = Venue.objects.get(id=self.cleaned_data.get('affiliation_object_id'))
        elif user_type == 'Organizer':
            affiliation = Exhibition.objects.get(id=self.cleaned_data.get('affiliation_object_id'))
        else:
            affiliation = Booth.objects.get(id=self.cleaned_data.get('affiliation_object_id'))

        parent_unit = SpaceUnit.objects.get(id=parent_id)
        space_unit.floor = floor
        space_unit.parent_unit = parent_unit
        space_unit.affiliation_content_type = ContentType.objects.get_for_model(affiliation)
        space_unit.affiliation_object_id = affiliation.pk

        if commit:
            space_unit.save()
        return space_unit
