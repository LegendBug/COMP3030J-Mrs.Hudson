from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from Booth.models import Booth
from Exhibition.models import Exhibition
from Inventory.forms import EditInventoryCategoryForm, CreateInventoryCategoryForm
from Inventory.models import InventoryCategory, Item
from Venue.models import Venue
from django.contrib.contenttypes.models import ContentType


@login_required
def inventory(request):
    user_type = 'Manager' if hasattr(request.user, 'manager') \
        else 'Organizer' if hasattr(request.user, 'organizer') \
        else 'Exhibitor' if hasattr(request.user, 'exhibitor') \
        else 'Guest'  # 根据用户的类型,获取与该用户关联的所有Item
    add_inventory_form = CreateInventoryCategoryForm()
    if user_type == 'Manager':
        venue = Venue.objects.filter(pk=request.session['venue_id']).first()
        venue_items = Item.objects.filter(content_type=ContentType.objects.get_for_model(venue), object_id=venue.id)
        all_categories = InventoryCategory.objects.all()  # 获取所有InventoryCategory
        for category in all_categories:  # 为每个类别计算属于该场馆的Item数量
            category.items_count = venue_items.filter(category=category).count()
        return render(request, 'Inventory/inventory.html',
                      {'venue': venue, 'categories': all_categories, 'user_type': user_type,
                       'add_inventory_form': add_inventory_form})
    elif user_type == 'Organizer':
        exhibition = Exhibition.objects.filter(1).first()  # TODO 假数据,临时写死
        exhibition_items = Item.objects.filter(content_type=ContentType.objects.get_for_model(exhibition),
                                               object_id=exhibition.id)
        all_categories = InventoryCategory.objects.all()  # 获取所有InventoryCategory
        for category in all_categories:  # 为每个类别计算属于该场馆的Item数量
            category.items_count = exhibition_items.filter(category=category).count()
        return render(request, 'Inventory/inventory.html',
                      {'exhibition': exhibition, 'categories': all_categories, 'user_type': user_type,
                       'add_inventory_form': add_inventory_form})
    elif user_type == 'Exhibitor':
        booth = Booth.objects.filter(1).first()  # TODO 假数据,临时写死
        booth_items = Item.objects.filter(content_type=ContentType.objects.get_for_model(booth),
                                          object_id=booth.id)
        all_categories = InventoryCategory.objects.all()  # 获取所有InventoryCategory
        for category in all_categories:  # 为每个类别计算属于该场馆的Item数量
            category.items_count = booth_items.filter(category=category).count()
        return render(request, 'Inventory/inventory.html',
                      {'booth': booth, 'categories': all_categories, 'user_type': user_type,
                       'add_inventory_form': add_inventory_form})
    else:  # 未登录的游客
        return JsonResponse({'message': 'Unauthorized'}, status=401)


def category_detail_view(request, category_id):
    venue_id = 1
    venue = get_object_or_404(Venue, pk=venue_id)
    category = get_object_or_404(InventoryCategory, pk=category_id)
    items = Item.objects.filter(object_id=venue_id, category=category)

    return render(request, 'Inventory/category_detail.html', {
        'venue': venue,
        'category': category,
        'items': items
    })


def edit_inventory_category(request, category_id):
    category = get_object_or_404(InventoryCategory, pk=category_id)
    if request.method == 'POST':
        form = EditInventoryCategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect('Inventory:venue-inventory')  # 重定向到某个合适的页面
    else:
        form = EditInventoryCategoryForm(instance=category)
    return render(request, 'Inventory/edit_category.html', {'form': form})


@login_required
def delete_inventory_category(request, category_id):
    category = get_object_or_404(InventoryCategory, pk=category_id)
    category.delete()  # 这会级联删除所有相关的 Item 对象，如果在模型中设置了 `on_delete=models.CASCADE`
    return redirect('Inventory:venue-inventory')  # 重定向到列表页
