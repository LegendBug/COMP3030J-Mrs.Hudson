from uuid import uuid4
from User.models import Message, Manager
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django import forms
from Exhibition.models import Exhibition, ExhibitionApplication
from Layout.models import SpaceUnit, KonvaElement
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, date
from User.models import Organizer, MessageDetail
from Venue.models import Venue
from django.contrib.contenttypes.models import ContentType
import json


class ExhibApplicationForm(forms.Form):
    # 关联的场馆ID
    venue_id = forms.IntegerField(widget=forms.HiddenInput())
    exhib_name = forms.CharField(widget=forms.TextInput(attrs={'id': 'exhibName'}), max_length=50, required=True,
                                 label='Exhibition Name')
    exhib_description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'id': 'exhibDescription'}),
                                        max_length=500, required=True, label='Exhibition Description')
    # 精确到分钟
    exhib_start_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'id': 'exhibStartAt', 'type': 'datetime-local', 'step': 60}), required=True,
        label="Start Date")
    exhib_end_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'id': 'exhibEndAt', 'type': 'datetime-local', 'step': 60}), required=True,
        label="End Date")
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
        self.fields['exhib_start_at'].initial = date.today()
        self.fields['exhib_sectors'].label_from_instance = lambda obj: f"{obj.name}"
        # 设置Sectors为某一场馆的SpaceUnits
        affiliation_object_id = self.initial.get('affiliation_object_id')
        affiliation_content_type = self.initial.get('affiliation_content_type')
        if affiliation_object_id and affiliation_content_type:
            self.fields['exhib_sectors'].queryset = SpaceUnit.objects.filter(
                affiliation_object_id=affiliation_object_id,
                affiliation_content_type=affiliation_content_type,
                available=True)
        else:
            # 如果没有提供venue_id, 则默认不显示任何选项
            self.fields['exhib_sectors'].queryset = SpaceUnit.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        exhib_start_at = cleaned_data.get('exhib_start_at')
        exhib_end_at = cleaned_data.get('exhib_end_at')
        exhib_sectors = cleaned_data.get('exhib_sectors')

        # 检查开始日期和结束日期是否都不为 None
        if exhib_start_at is not None and exhib_end_at is not None:
            # 验证开始日期是否早于结束日期
            if exhib_start_at >= exhib_end_at:
                self.add_error('exhib_start_at', 'Start date must be earlier than end date.')

        # 保证用户预约区域不会与已有展会冲突
        if exhib_sectors is not None:
            # 遍历当前选中的sector
            for sector in exhib_sectors:
                # 遍历该sector全部的复制品
                occupied_units = sector.occupied_units.filter(
                    affiliation_content_type=ContentType.objects.get_for_model(Exhibition))
                for occupied_unit in occupied_units:
                    if (occupied_unit.affiliation.start_at <= exhib_start_at <= occupied_unit.affiliation.end_at or
                            occupied_unit.affiliation.start_at <= exhib_end_at <= occupied_unit.affiliation.end_at):
                        self.add_error('exhib_sectors',
                                       f"Sorry☹️, '{sector.name}' is occupied during this period. "
                                       f"Please choose a different time or sector.")
                        break
        return cleaned_data

    def create_application(self, request):
        """使用表单数据创建新的展览申请，包括展览本身和相关的展览单元。"""
        with transaction.atomic():  # 使用事务确保操作的原子性
            venue = Venue.objects.get(pk=self.cleaned_data['venue_id'])
            organizer = Organizer.objects.get(detail=request.user)

            # 创建新的展览
            new_exhibition = Exhibition.objects.create(
                name=self.cleaned_data['exhib_name'],
                description=self.cleaned_data['exhib_description'],
                start_at=self.cleaned_data['exhib_start_at'],
                end_at=self.cleaned_data['exhib_end_at'],
                image=self.cleaned_data['exhib_image'],
                organizer=organizer,
                venue=venue
            )

            # 为选中的SpaceUnit创建副本，并关联到新的Exhibition
            for sector in self.cleaned_data['exhib_sectors']:
                new_sector = SpaceUnit.objects.create(
                    name=sector.name,
                    description=sector.description,
                    floor=sector.floor,
                    inherit_from=sector,
                    parent_unit=None,  # 可以根据实际情况调整
                    available=False,
                    affiliation_content_type=ContentType.objects.get_for_model(Exhibition),
                    affiliation_object_id=new_exhibition.pk
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

            # 创建展览申请和相关消息
            new_exhib_application = ExhibitionApplication.objects.create(
                applicant=request.user,
                description=self.cleaned_data['exhib_description'],
                exhibition=new_exhibition
            )
            new_message = Message.objects.create(
                title=f"New Exhibition Application for '{new_exhibition.name}'",
                sender=request.user,
                recipient=Manager.objects.first().detail
            )
            application_type = ContentType.objects.get_for_model(ExhibitionApplication)
            MessageDetail.objects.create(
                message=new_message,
                content=self.cleaned_data['message_content'],
                application_object_id=new_exhib_application.id,
                application_content_type=application_type
            )
            return new_exhibition  # 或者返回创建的展览对象，根据需要调整


class FilterExhibitionsForm(forms.Form):
    name = forms.CharField(required=False, label="Exhibition Name")
    venue_id = forms.IntegerField(widget=forms.HiddenInput())
    start_at = forms.DateField(required=False, label="Start Date",
                               widget=forms.DateInput(attrs={'type': 'date'}))
    end_at = forms.DateField(required=False, label="End Date",
                             widget=forms.DateInput(attrs={'type': 'date'}))
    organizer_name = forms.CharField(required=False, label="Organizer Name")

    def clean(self):
        cleaned_data = super().clean()
        start_at = cleaned_data.get("start_at")
        end_at = cleaned_data.get("end_at")
        venue_id = cleaned_data.get("venue_id")
        if start_at and end_at:
            if end_at <= start_at:
                raise ValidationError(_("End date must be after the start date."))
        if not Venue.objects.filter(pk=venue_id).exists():
            raise ValidationError(_("Invalid venue ID."))
        return cleaned_data

    def filter(self):
        if not self.is_valid():
            return Exhibition.objects.none()  # 如果表单数据无效，则返回空查询集

        cleaned_data = self.cleaned_data
        name = cleaned_data.get('name')
        venue_id = cleaned_data.get('venue_id')
        start_at = cleaned_data.get('start_at')
        end_at = cleaned_data.get('end_at')
        organizer_name = cleaned_data.get('organizer_name')

        # 建立基础查询
        qs = Exhibition.objects.all().filter(venue_id=venue_id)
        if name:
            qs = qs.filter(name__icontains=name)
        if start_at:
            start_datetime = timezone.make_aware(datetime.combine(start_at, datetime.min.time()))
            qs = qs.filter(start_at__gte=start_datetime)
        if end_at:
            end_datetime = timezone.make_aware(datetime.combine(end_at, datetime.max.time()))
            qs = qs.filter(end_at__lte=end_datetime)
        if organizer_name:
            qs = qs.filter(organizer__detail__username__icontains=organizer_name)
        return qs
