import datetime

from django import forms

from Layout.models import SpaceUnit


class BoothApplicationForm(forms.Form):
    exhib_id = forms.IntegerField(widget=forms.HiddenInput())
    booth_name = forms.CharField(widget=forms.TextInput(attrs={'id': 'boothName'}), max_length=50, required=True,
                                 label='Booth Name')
    booth_description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'id': 'boothDescription'}),
                                        max_length=500, required=True, label='Booth Description')
    booth_image = forms.ImageField(widget=forms.FileInput(attrs={'id': 'boothImage'}), required=True, label="Image")
    # 展台只有一个Sector(Booth模型实际能接受多个Sector,但是这里只允许选择一个)
    booth_sector = forms.ModelChoiceField(
        queryset=SpaceUnit.objects.none(),
        widget=forms.Select(attrs={'id': 'boothSector'}),
        required=True,
        label="Booth Sector"
    )
    message_content = forms.CharField(max_length=500,
                                      required=True,
                                      widget=forms.Textarea(attrs={'rows': 3, 'id': 'messageContent'}),
                                      label="Additional Message")

    def __init__(self, *args, **kwargs):
        super(BoothApplicationForm, self).__init__(*args, **kwargs)
        self.fields['booth_sector'].label_from_instance = lambda obj: f"{obj.name}"
        # 设置Sectors为某一展览的SpaceUnit
        affiliation_object_id = self.initial.get('affiliation_object_id')
        affiliation_content_type = self.initial.get('affiliation_content_type')
        if affiliation_object_id and affiliation_content_type:
            self.fields['booth_sector'].queryset = SpaceUnit.objects.filter(
                affiliation_object_id=affiliation_object_id,
                affiliation_content_type=affiliation_content_type,
                available=True
            )
        else:
            self.fields['booth_sector'].queryset = SpaceUnit.objects.all()
