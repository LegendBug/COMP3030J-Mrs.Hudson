from django import forms
from Booth.models import Booth
from Layout.models import SpaceUnit
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, date


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


class FilterBoothsForm(forms.Form):
    name = forms.CharField(required=False, label="Booth Name")
    exhibition_id = forms.IntegerField(widget=forms.HiddenInput())
    start_at = forms.DateField(required=False, label="Start Date",
                               widget=forms.DateInput(attrs={'type': 'date'}))
    end_at = forms.DateField(required=False, label="End Date",
                             widget=forms.DateInput(attrs={'type': 'date'}))
    exhibitor_name = forms.CharField(required=False, label="Exhibitor Name")

    def clean(self):
        cleaned_data = super().clean()
        start_at = cleaned_data.get("start_at")
        end_at = cleaned_data.get("end_at")

        if start_at and end_at:
            if end_at <= start_at:
                raise ValidationError(_("End date must be after the start date."))
        return cleaned_data

    def filter(self):
        if not self.is_valid():
            return Booth.objects.none()  # 如果表单数据无效，则返回空查询集

        cleaned_data = self.cleaned_data
        name = cleaned_data.get('name')
        exhibition_id = cleaned_data.get('exhibition_id')
        start_at = cleaned_data.get('start_at')
        end_at = cleaned_data.get('end_at')
        exhibitor_name = cleaned_data.get('exhibitor_name')

        # 建立基础查询
        qs = Booth.objects.all().filter(exhibition_id=exhibition_id)
        if name:
            qs = qs.filter(name__icontains=name)
        if start_at:
            start_datetime = timezone.make_aware(datetime.combine(start_at, datetime.min.time()))
            qs = qs.filter(start_at__gte=start_datetime)
        if end_at:
            end_datetime = timezone.make_aware(datetime.combine(end_at, datetime.max.time()))
            qs = qs.filter(end_at__lte=end_datetime)
        if exhibitor_name:
            qs = qs.filter(organizer__detail__username__icontains=exhibitor_name)
        return qs
