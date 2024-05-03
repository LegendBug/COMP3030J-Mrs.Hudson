from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from Booth.models import Booth
from Exhibition.models import Exhibition
from Inventory.forms import EditInventoryCategoryForm, CreateInventoryCategoryForm, EditItemForm
from Inventory.models import InventoryCategory, Item
from Venue.models import Venue


@login_required
def inventory(request):
    user_type = 'Manager' if hasattr(request.user, 'manager') \
        else 'Organizer' if hasattr(request.user, 'organizer') \
        else 'Exhibitor' if hasattr(request.user, 'exhibitor') \
        else 'Guest'  # 根据用户的类型,获取与该用户关联的所有Item
    # 获取current_access, current_access是一个Venue/Exhibition/Booth实例, 它代表着用户当前所访问的Venue/Exhibition/Booth
    if user_type == 'Manager':
        current_access = Venue.objects.filter(pk=request.session['venue_id']).first()
    elif user_type == 'Organizer':
        current_access = Exhibition.objects.filter(pk=1).first()  # TODO 假数据,临时写死
    elif user_type == 'Exhibitor':
        current_access = Booth.objects.filter(pk=1).first()  # TODO 假数据,临时写死
    else:  # 未登录的游客
        return redirect('User:login')
    if request.method == 'POST':
        submitted_form = CreateInventoryCategoryForm(request.POST, request.FILES, origin=current_access)
        if submitted_form.is_valid():
            category = submitted_form.save()
            if category:
                return JsonResponse({'success': 'Category and items created'}, status=201)
            else:
                return JsonResponse({'errors': 'Failed to create category and items'}, status=500)
        else:
            # TODO 存在bug,需要修改  return JsonResponse({'errors': submitted_form.errors.as_json()}, status=400)
            return JsonResponse(
                {'errors': "There is an error in the content you filled in, please correct it and submit again!"},
                status=400)
    else:  # 如果是 GET 请求，只需返回一个空表单
        add_inventory_form = CreateInventoryCategoryForm(origin=current_access)
        # 通过当前访问的Venue/Exhibition/Booth中的所有Item,获取所有的Category并统计每个Category下的Item数量
        current_items = current_access.items.all()
        current_categories = {}
        for current_item in current_items:
            # 如果current_item.category不在current_categories中,则添加如果current_item.category进入字典,并为其值初始化为1
            if current_item.category not in current_categories:
                current_categories[current_item.category] = 1
            else:
                current_categories[current_item.category] = current_categories[current_item.category] + 1
        # 查找那些origin为当前访问的Venue/Exhibition/Booth的InventoryCategory,并统计它们的数量, 以避免这些Category被重复创建
        existing_categories = current_access.inventory_categories.all()
        for existing_category in existing_categories:
            if existing_category not in current_categories:
                current_categories[existing_category] = 0
        # 将字典中的Category按照名称排序后存入数组,同时为每个Category添加一个quantity属性来记录该Category下的Item数量
        categories = []
        for category, quantity in current_categories.items():
            category.items_quantity = quantity
            categories.append(category)
        return render(request, 'Inventory/inventory.html',
                      {
                          'user_type': user_type,
                          'current_access': current_access,
                          'categories': current_categories,
                          'add_inventory_form': add_inventory_form
                      })


def category_detail_view(request, category_id):
    user_type = 'Manager' if hasattr(request.user, 'manager') \
        else 'Organizer' if hasattr(request.user, 'organizer') \
        else 'Exhibitor' if hasattr(request.user, 'exhibitor') \
        else 'Guest'  # 根据用户的类型,获取与该用户关联的所有Item
    current_access = Venue.objects.filter(pk=request.session['venue_id']).first()
    category = InventoryCategory.objects.filter(pk=category_id).first()
    items = category.items.all()

    return render(request, 'Inventory/category_detail.html', {
        'current_access': current_access,
        'category': category,
        'items': items,
        'user_type': user_type
    })


def edit_inventory_category(request, category_id):
    category = get_object_or_404(InventoryCategory, pk=category_id)
    if request.method == 'POST':
        form = EditInventoryCategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect('Inventory:inventory')  # 重定向到某个合适的页面
    else:
        form = EditInventoryCategoryForm(instance=category)
    return render(request, 'Inventory/edit_category.html', {'form': form})


@login_required
def delete_inventory_category(request, category_id):
    category = get_object_or_404(InventoryCategory, pk=category_id)
    user_type = request.session.get('user_type', 'Guest')  # 从会话中获取用户类型

    # 检查 category 下是否有正在使用的 item
    if category.items.filter(is_using=True).exists():
        messages.error(request, "Some items are currently in use and cannot be deleted.")
        return redirect('Inventory:inventory')

    # 处理不同用户类型的权限和逻辑
    if user_type == 'Manager' or (user_type in ['Organizer', 'Exhibitor'] and not category.is_public):
        category.delete()
        messages.success(request, "Category deleted successfully.")
    else:
        messages.error(request,
                       "Cannot delete a public category. Please go to category details to return or delete items.")

    return redirect('Inventory:inventory')


@login_required
def item_detail_view(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    return render(request, 'Inventory/item_detail.html', {'item': item})


@login_required
def edit_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if request.method == 'POST':
        form = EditItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('Inventory:inventory')
    else:
        form = EditItemForm(instance=item)
    return render(request, 'Inventory/edit_item.html', {'form': form})


# @login_required
# def delete_item(request, item_id):
#     item = get_object_or_404(Item, pk=item_id)
#     item.delete()
#     return redirect('Inventory:inventory')


@login_required
def return_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(Item, pk=item_id)
        # 修改 affiliation 至 origin
        item.affiliation = item.category.origin
        item.save()
        messages.success(request, "Item returned successfully.")
        return redirect('Inventory:category_detail', category_id=item.category.id)


@login_required
def delete_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(Item, pk=item_id)
        item.delete()
        messages.success(request, "Item deleted successfully.")
        return redirect('Inventory:category_detail', category_id=item.category.id)


def create_res_application(request):
    if request.method == 'POST':
        try:
            form = ResourceApplicationForm(request.POST, request.FILES)
            if not form.is_valid():
                first_error_key, first_error_messages = list(form.errors.items())[0]
                first_error_message = first_error_key + ': ' + first_error_messages[0]
                return JsonResponse({'error': first_error_message}, status=400)
            venue_id = form.cleaned_data.get('venue_id')
            name = form.cleaned_data.get('res_name')
            description = form.cleaned_data.get('res_description')
            start_at = form.cleaned_data.get('res_start_at')
            end_at = form.cleaned_data.get('res_end_at')
            image = form.cleaned_data.get('res_image')
            sectors = form.cleaned_data.get('res_sectors')
            content = form.cleaned_data.get('message_content')
            venue = Venue.objects.get(pk=venue_id)
            organizer = Organizer.objects.get(detail=request.user)
            new_resource = Resource.objects.create(
                name=name, description=description, start_at=start_at, end_at=end_at,
                image=image, organizer=organizer, venue=venue
            )
            new_resource.sectors.set(sectors)
            new_res_application = ResourceApplication.objects.create(applicant=request.user,
                                                                     description=description,
                                                                     resource=new_resource)
            new_resource.application = new_res_application
            new_resource.save()
            new_res_application.save()
            new_message = Message.objects.create(title='New Resource Application for ' + name, sender=request.user,
                                                 recipient=Manager.objects.first().detail)
            application_type = ContentType.objects.get_for_model(new_res_application)
            new_message_detail = MessageDetail.objects.create(message=new_message, content=content,
                                                              application_object_id=new_res_application.id,
                                                              application_content_type=application_type)
            new_message.detail = new_message_detail
            new_message.save()
            return JsonResponse({'success': 'Resource application created successfully!'}, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Internal Server Error', 'details': str(e)}, status=500)
    else:
        return HttpResponseNotAllowed(['POST'])
