from django import forms
from Inventory.models import InventoryCategory

class EditInventoryCategoryForm(forms.ModelForm):
    class Meta:
        model = InventoryCategory
        fields = ['name', 'description', 'is_private', 'cost', 'image']

class CreateInventoryCategoryForm(forms.ModelForm):
    class Meta:
        model = InventoryCategory
        fields = ['name', 'description', 'is_private', 'cost', 'image']
        # TODO 需要修改