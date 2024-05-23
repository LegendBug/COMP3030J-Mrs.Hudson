import json
from django.core.files.base import ContentFile
from django import forms
from django.db import transaction
from User.models import Message, Manager, Exhibitor, MessageDetail
from Booth.models import Booth, BoothApplication
from Exhibition.models import Exhibition
from Layout.models import SpaceUnit, KonvaElement
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, date
from django.contrib.contenttypes.models import ContentType
from uuid import uuid4


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

    def clean(self):
        cleaned_data = super().clean()
        exhib_id = cleaned_data.get('exhib_id')
        sector = cleaned_data.get('booth_sector')

        exhibition = Exhibition.objects.get(id=exhib_id)
        booth_start_at = exhibition.start_at
        booth_end_at = exhibition.end_at
        # 保证用户预约区域不会与已有展会冲突
        if sector is not None:
            occupied_units = sector.occupied_units.filter(
                affiliation_content_type=ContentType.objects.get_for_model(Booth))
            for occupied_unit in occupied_units:
                if (occupied_unit.affiliation.start_at <= booth_start_at <= occupied_unit.affiliation.end_at or
                        occupied_unit.affiliation.start_at <= booth_end_at <= occupied_unit.affiliation.end_at):
                    self.add_error('booth_sector',
                                   f"Sorry☹️, '{sector.name}' is occupied during this period. "
                                   f"Please choose a different time or sector.")
                    break
        return cleaned_data

    def create_application(self, request):
        """使用表单的清理数据创建新的展台及其申请。"""
        with transaction.atomic():  # 确保操作的原子性
            exhibition = Exhibition.objects.get(id=self.cleaned_data['exhib_id'])
            exhibitor = Exhibitor.objects.get(detail=request.user)
            sector = self.cleaned_data['booth_sector']

            # 创建新展台
            new_booth = Booth.objects.create(
                name=self.cleaned_data['booth_name'],
                description=self.cleaned_data['booth_description'],
                image=self.cleaned_data['booth_image'],
                exhibitor=exhibitor,
                exhibition=exhibition,
                start_at=exhibition.start_at,  # 假设展台共享展览时间
                end_at=exhibition.end_at
            )
            new_sector = SpaceUnit.objects.create(
                name=sector.name,
                description=sector.description,
                floor=sector.floor,
                inherit_from=sector,
                parent_unit=None,  # 可以根据实际情况调整
                available=False,
                affiliation_content_type=ContentType.objects.get_for_model(Booth),
                affiliation_object_id=new_booth.pk
            )
            # 复制KonvaElement到新的SpaceUnit
            for element in sector.elements.all():
                new_element = KonvaElement.objects.create(
                    name=element.name,
                    layer=new_sector,
                    type=element.type,
                    data=element.data,
                    transformable=element.transformable
                )

                # Update the JSON data to include the new element's id
                updated_element_data = json.loads(element.data)
                updated_element_data["attrs"]["id"] = f"{new_element.pk}"
                new_element.data = json.dumps(updated_element_data)

                if element.image:
                    with element.image.open() as image_file:
                        content = image_file.read()
                    new_filename = f'{uuid4()}.{element.image.name.split(".")[-1]}'
                    new_image_file = ContentFile(content)
                    new_element.image.save(new_filename, new_image_file, save=True)

                new_element.save()

            # 创建展台申请
            new_booth_application = BoothApplication.objects.create(
                applicant=request.user,
                description=self.cleaned_data['booth_description'],
                booth=new_booth
            )
            new_booth.booth_application = new_booth_application
            new_booth.save()
            new_booth_application.save()

            # 可选创建和处理相关消息
            new_message = Message.objects.create(
                title="New Booth Application for '" + exhibition.name + ': ' + self.cleaned_data.get(
                    'booth_name') + "'",
                sender=request.user,
                recipient=Manager.objects.first().detail
            )
            application_type = ContentType.objects.get_for_model(BoothApplication)
            MessageDetail.objects.create(
                message=new_message,
                content=self.cleaned_data['message_content'],
                application_object_id=new_booth_application.id,
                application_content_type=application_type
            )
            new_message.save()

            return new_booth  # 返回新展台对象以便进一步处理


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
