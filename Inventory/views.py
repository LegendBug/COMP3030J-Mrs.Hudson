from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from Inventory.models import InventoryCategory, Item
from Venue.models import Venue
from django import forms

@login_required
def venue_inventory_view(request):
    # user = request.user
    # if hasattr(user,'manager'):
    #     return HttpResponseForbidden("You do not have permission to view this page.")
    venue_id = 1
    # 获取当前场馆实例
    venue = Venue.objects.get(pk=venue_id)

    # 获取与该场馆关联的所有Item
    items = Item.objects.filter(object_id=venue_id)

    # 获取所有InventoryCategory
    categories = InventoryCategory.objects.all()

    # 为每个类别计算属于该场馆的Item数量
    for category in categories:
        category.items_count = items.filter(category=category).count()

    context = {'categories': categories}
    return render(request, 'Inventory/Venue_materials.html', context)



def category_detail_view(request,category_id):
    venue_id = 1
    venue = get_object_or_404(Venue, pk=venue_id)
    category = get_object_or_404(InventoryCategory, pk=category_id)
    items = Item.objects.filter(object_id=venue_id, category=category)

    return render(request, 'Inventory/category_detail.html', {
        'venue': venue,
        'category': category,
        'items': items
    })

class InventoryCategoryForm(forms.ModelForm):
    class Meta:
        model = InventoryCategory
        fields = ['name', 'description', 'is_private', 'cost', 'image']

def edit_inventory_category(request, category_id):
    category = get_object_or_404(InventoryCategory, pk=category_id)
    if request.method == 'POST':
        form = InventoryCategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect('Inventory:venue-inventory')  # 重定向到某个合适的页面
    else:
        form = InventoryCategoryForm(instance=category)
    return render(request, 'Inventory/edit_category.html', {'form': form})

@login_required
def delete_inventory_category(request, category_id):
    category = get_object_or_404(InventoryCategory, pk=category_id)
    category.delete()  # 这会级联删除所有相关的 Item 对象，如果在模型中设置了 `on_delete=models.CASCADE`
    return redirect('Inventory:venue-inventory')  # 重定向到列表页