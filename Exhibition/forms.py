import datetime
from django.utils.translation import gettext_lazy as _
from django import forms

from Exhibition.models import Exhibition
from Layout.models import SpaceUnit
from django.core.exceptions import ValidationError


class ExhibApplicationForm(forms.Form):
    # 关联的场馆ID
    venue_id = forms.IntegerField(widget=forms.HiddenInput())
    exhib_name = forms.CharField(widget=forms.TextInput(attrs={'id': 'exhibName'}), max_length=50, required=True,
                                 label='Exhibition Name')
    exhib_description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'id': 'exhibDescription'}),
                                        max_length=500, required=True, label='Exhibition Description')
    # 精确到分钟
    exhib_start_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'id': 'exhibStartAt', 'type': 'datetime-local', 'step': 60}),
        required=True, label="Start Date")
    exhib_end_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'id': 'exhibEndAt', 'type': 'datetime-local', 'step': 60}),
        required=True, label="End Date")
    exhib_image = forms.ImageField(widget=forms.FileInput(attrs={'id': 'exhibImage'}), required=True, label="Image")
    exhib_sectors = forms.ModelMultipleChoiceField(
        queryset=SpaceUnit.objects.none(),
        widget=forms.SelectMultiple(attrs={'id': 'exhibSectors'}),  # 设置为多选下拉框,
        required=True,
        label="Exhibition Sectors"  # 更改标签以表示多个选择
    )
    # 创建展览申请的附加说明
    message_content = forms.CharField(max_length=500,
                                      required=True,
                                      widget=forms.Textarea(attrs={'rows': 3, 'id': 'messageContent'}),
                                      label="Additional Message")

    def __init__(self, *args, **kwargs):
        super(ExhibApplicationForm, self).__init__(*args, **kwargs)
        # 设置默认日期为今天
        self.fields['exhib_start_at'].initial = datetime.date.today()
        self.fields['exhib_sectors'].label_from_instance = lambda obj: f"{obj.name}"
        # 设置Sectors为某一场馆的SpaceUnits
        affiliation_object_id = self.initial.get('affiliation_object_id')
        affiliation_content_type = self.initial.get('affiliation_content_type')
        if affiliation_object_id and affiliation_content_type:
            self.fields['exhib_sectors'].queryset = SpaceUnit.objects.filter(
                affiliation_object_id=affiliation_object_id,
                affiliation_content_type=affiliation_content_type)
        else:
            self.fields['exhib_sectors'].queryset = SpaceUnit.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        exhib_start_at = cleaned_data.get('exhib_start_at')
        exhib_end_at = cleaned_data.get('exhib_end_at')

        # 检查开始日期和结束日期是否都不为 None
        if exhib_start_at is not None and exhib_end_at is not None:
            # 验证开始日期是否早于结束日期
            if exhib_start_at >= exhib_end_at:
                self.add_error('exhib_start_at', 'Start date must be earlier than end date.')
        return cleaned_data


class FilterExhibitionsForm(forms.Form):
    name = forms.CharField(required=False, label="Exhibition Name")
    venue_id = forms.IntegerField(widget=forms.HiddenInput())
    start_at = forms.DateTimeField(required=False, label="Start Date",
                                   widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    end_at = forms.DateTimeField(required=False, label="End Date",
                                 widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    organizer = forms.CharField(required=False, label="Organizer Name")

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
            return Exhibition.objects.none()  # 如果表单数据无效，则返回空查询集

        cleaned_data = self.cleaned_data
        name = cleaned_data.get('name')
        venue_id = cleaned_data.get('venue_id')
        start_at = cleaned_data.get('start_at')
        end_at = cleaned_data.get('end_at')
        organizer = cleaned_data.get('organizer')

        # 建立基础查询
        qs = Exhibition.objects.all().filter(venue_id=venue_id)
        if name:
            qs = qs.filter(name__icontains=name)
        if start_at:
            qs = qs.filter(start_at__gte=start_at)
        if end_at:
            qs = qs.filter(end_at__lte=end_at)
        if organizer:
            qs = qs.filter(organizer__name__icontains=organizer)
        return qs
