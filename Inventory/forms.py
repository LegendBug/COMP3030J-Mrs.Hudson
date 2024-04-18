from django import forms
from django.db import transaction
from Booth.models import Booth
from Exhibition.models import Exhibition
from Inventory.models import InventoryCategory, Item
from django.contrib.contenttypes.models import ContentType


class EditInventoryCategoryForm(forms.ModelForm):
    class Meta:
        model = InventoryCategory
        fields = ['name', 'description', 'is_public', 'cost', 'image']


class CreateInventoryCategoryForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1, initial=1, required=True, label="Number of Items")
    power = forms.FloatField(required=False, label="Power Consumption(Optional)")
    water_consumption = forms.FloatField(required=False, label="Daily Water Consumption(Optional)")

    class Meta:
        model = InventoryCategory
        fields = ['name', 'description', 'is_public', 'cost', 'image', 'origin_content_type', 'origin_object_id']
        widgets = {
            'origin_content_type': forms.HiddenInput(),
            'origin_object_id': forms.HiddenInput(),
            'is_public': forms.CheckboxInput(),  # 确保is_public为必填，并使用复选框
        }

    def __init__(self, *args, **kwargs):  # 需要传入user和venue/exhibition/booth作为参数
        self.origin = kwargs.pop('origin', None)
        super(CreateInventoryCategoryForm, self).__init__(*args, **kwargs)
        if self.origin:
            self.fields['origin_content_type'].initial = ContentType.objects.get_for_model(type(self.origin))
            self.fields['origin_object_id'].initial = self.origin.pk
        self.fields['image'].required = True  # 确保image为必填
        self.fields['is_public'].required = True  # 确保is_public为必填

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

        quantity = self.cleaned_data.get('quantity')
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
