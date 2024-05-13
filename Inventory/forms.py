from django import forms
from django.db import transaction
from django.db.models import Count
from django.utils.timezone import now

from Booth.models import Booth
from Exhibition.models import Exhibition
from Inventory.models import InventoryCategory, Item
from django.contrib.contenttypes.models import ContentType
from django import forms

from Statistic.models import Usage
from . import models
from .models import Item


class EditInventoryCategoryForm(forms.ModelForm):
    class Meta:
        model = InventoryCategory
        fields = ['name', 'description', 'is_public', 'cost', 'image']


class CreateInventoryCategoryForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1, initial=1, required=True, label="Number of Initial Items")
    power = forms.FloatField(required=False, label="Power Consumption(Optional)")
    water_consumption = forms.FloatField(required=False, label="Daily Water Consumption(Optional)")

    class Meta:
        model = InventoryCategory
        fields = ['name', 'description', 'is_public', 'cost', 'image', 'origin_content_type', 'origin_object_id']
        widgets = {
            'origin_content_type': forms.HiddenInput(),
            'origin_object_id': forms.HiddenInput(),
            'is_public': forms.CheckboxInput(attrs={'class': 'hidden'}),  # 初始隐藏is_public字段
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):  # 需要传入user和venue/exhibition/booth作为参数
        self.origin = kwargs.pop('origin', None)
        super(CreateInventoryCategoryForm, self).__init__(*args, **kwargs)
        user_type = self.initial.get('user_type', 'Manager')

        # 如果是Manager, 则需要显示is_public字段
        if user_type == 'Manager':
            self.fields['is_public'].widget = forms.CheckboxInput()
            self.fields['is_public'].required = True
            self.fields['is_public'].initial = True
        else:  # 如果是其他用户, 则隐藏is_public字段
            self.fields['is_public'].widget = forms.HiddenInput()
            self.fields['is_public'].initial = False

        if self.origin:
            self.fields['origin_content_type'].initial = ContentType.objects.get_for_model(type(self.origin))
            self.fields['origin_object_id'].initial = self.origin.pk

        self.fields['name'].label = "Resource Name"
        self.fields['description'].label = "Resource Description"
        self.fields['image'].required = True  # 确保image为必填

    def clean_cost(self):
        cost = self.cleaned_data.get('cost')
        if cost is not None and cost < 0:
            raise forms.ValidationError("Cost must be a non-negative number.")
        return cost

    def clean_power(self):
        power = self.cleaned_data.get('power')
        if power is not None and power < 0:
            raise forms.ValidationError("Power consumption must be a non-negative number.")
        return power

    def clean_water_consumption(self):
        water_consumption = self.cleaned_data.get('water_consumption')
        if water_consumption is not None and water_consumption < 0:
            raise forms.ValidationError("Water consumption must be a non-negative number.")
        return water_consumption

    @transaction.atomic
    def save(self, commit=True):
        category = super(CreateInventoryCategoryForm, self).save(commit=False)

        # 保存InventoryCategory实例
        category.origin = self.origin
        if commit:
            category.save()

        quantity = self.cleaned_data.get('quantity', 1)
        power = self.cleaned_data.get('power', None)
        water_consumption = self.cleaned_data.get('water_consumption', None)

        # 创建Item实例
        items = [
            Item(
                name=category.name,
                power=power,
                water_consumption=water_consumption,
                category=category,
                affiliation_content_type=self.cleaned_data['origin_content_type'],
                affiliation_object_id=self.cleaned_data['origin_object_id'],

            ) for _ in range(quantity)
        ]
        if commit:
            Item.objects.bulk_create(items)
        return category


class EditItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'is_using', 'is_damaged', 'power', 'water_consumption', 'location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_using': forms.CheckboxInput(),
            'is_damaged': forms.CheckboxInput(),
            'power': forms.NumberInput(attrs={'class': 'form-control'}),
            'water_consumption': forms.NumberInput(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            # 检查原数据库表中的is_using字段是否发生变更
            original_instance = Item.objects.get(pk=instance.pk)
            instance.save()
            # if original_instance.is_using != instance.is_using:
            #     print('end')

            if instance.is_using and not original_instance.is_using:
                # is_using 从 False 变为 True，开始新的使用
                Usage.objects.create(
                    item=instance,
                    start_time=now(),
                    location_content_type=instance.affiliation_content_type,
                    location_object_id=instance.affiliation_object_id
                )
            elif not instance.is_using and original_instance.is_using:
                # is_using 从 True 变为 False，结束当前的使用
                usage = Usage.objects.filter(item=instance).latest('start_time')
                usage.end_time = now()
                duration_hours = (usage.end_time - usage.start_time).total_seconds() / 3600
                usage.water_consumption = duration_hours * instance.water_consumption if instance.water_consumption else None
                usage.power_consumption = duration_hours * instance.power if instance.power else None
                usage.save()
        return instance


class ResApplicationForm(forms.Form):
    # 关联的场馆ID
    booth_id = forms.IntegerField(widget=forms.HiddenInput())
    category = forms.ModelChoiceField(
        queryset=InventoryCategory.objects.none(),  # 初始为空，稍后设置
        widget=forms.Select(attrs={'id': 'category'}),
        required=True,
        label="Resource Category"
    )
    quantity = forms.IntegerField(min_value=1, initial=1, required=True, label="Quantity")
    # 创建资源申请的附加说明
    message_content = forms.CharField(max_length=500,
                                      required=True,
                                      widget=forms.Textarea(attrs={'rows': 3, 'id': 'messageContent'}),
                                      label="Additional Message")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].label_from_instance = lambda obj: obj.name
        origin_object_id = self.initial.get('origin_object_id')
        origin_content_type = self.initial.get('origin_content_type')
        print('origin_object_id:', origin_object_id)
        print('origin_content_type:', origin_content_type)
        if origin_object_id and origin_content_type:
            # 获取所有与此origin相关联的、items数量不为0的InventoryCategory
            self.fields['category'].queryset = InventoryCategory.objects.filter(
                origin_content_type_id=origin_content_type,
                origin_object_id=origin_object_id
            ).annotate(item_count=Count('items')).filter(item_count__gt=0)
            print('category success:', self.fields['category'].queryset)
        else:
            self.fields['category'].queryset = InventoryCategory.objects.all()
            print('category fail:', self.fields['category'].queryset)
