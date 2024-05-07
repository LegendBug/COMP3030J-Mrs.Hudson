from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404, redirect

from Booth.models import Booth
from Exhibition.models import Exhibition
from Inventory.forms import EditInventoryCategoryForm, CreateInventoryCategoryForm, EditItemForm, ResApplicationForm
from Inventory.models import InventoryCategory, Item, ResourceApplication
from User.models import Message, Manager, MessageDetail
from Venue.models import Venue


@login_required
def inventory(request, space_type, space_id):
    # 获取用户类型
    user_type = 'Manager' if hasattr(request.user, 'manager') \
        else 'Organizer' if hasattr(request.user, 'organizer') \
        else 'Exhibitor'
    # 检查用户类型和空间类型是否匹配，current_access是一个Venue/Exhibition/Booth实例, 它代表着用户当前所访问的Venue/Exhibition/Booth
    if space_type == 'venue':
        if user_type != 'Manager':
            return JsonResponse({'error': 'Permission denied!'}, status=403)
        current_access = Venue.objects.filter(pk=space_id).first()
    elif space_type == 'exhibition':
        if user_type not in ['Manager', 'Organizer']:
            return JsonResponse({'error': 'Permission denied!'}, status=403)
        current_access = Exhibition.objects.filter(pk=space_id).first()
    elif space_type == 'booth':
        current_access = Booth.objects.filter(pk=space_id).first()
    else:
        return JsonResponse({'error': 'Invalid space type!'}, status=400)
    request.session['space_type'] = space_type
    request.session['space_id'] = space_id

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

        # 申请库存表单
        if space_type == 'booth':
            # 获取当前展区可见的全部Category
            current_venue = current_access.exhibition.venue
            affiliation_type = ContentType.objects.get_for_model(current_venue)
            application_form = ResApplicationForm(
                initial={'origin_content_type': affiliation_type, 'origin_object_id': current_venue.pk})
        else:
            application_form = None
        return render(request, 'Inventory/inventory.html',
                      {
                          'user_type': user_type,
                          'current_access': current_access,
                          'categories': categories,
                          'space_type': space_type,
                          'space_id': space_id,
                          'add_inventory_form': add_inventory_form,
                          'application_form': application_form
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
            space_type = request.session.get('space_type')
            space_id = request.session.get('space_id')
            return redirect('Inventory:inventory', space_type=space_type, space_id=space_id)
    else:
        form = EditInventoryCategoryForm(instance=category)
    return render(request, 'Inventory/edit_category.html', {'form': form})


@login_required
def delete_inventory_category(request, category_id):
    category = get_object_or_404(InventoryCategory, pk=category_id)
    user_type = request.session.get('user_type', 'Guest')  # 从会话中获取用户类型
    space_type = request.session.get('space_type')
    space_id = request.session.get('space_id')

    # 检查 category 下是否有正在使用的 item
    if category.items.filter(is_using=True).exists():
        messages.error(request, "Some items are currently in use and cannot be deleted.")
        return redirect('Inventory:inventory', space_type=space_type, space_id=space_id)

    # 处理不同用户类型的权限和逻辑
    if user_type == 'Manager' or (user_type in ['Organizer', 'Exhibitor'] and not category.is_public):
        category.delete()
        messages.success(request, "Category deleted successfully.")
    else:
        messages.error(request,
                       "Cannot delete a public category. Please go to category details to return or delete items.")
    return redirect('Inventory:inventory', space_type=space_type, space_id=space_id)


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
            space_type = request.session.get('space_type')
            space_id = request.session.get('space_id')
            return redirect('Inventory:inventory', space_type=space_type, space_id=space_id)
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


@login_required
def create_res_application(request):
    if request.method == 'POST':
        try:
            if not hasattr(request.user, 'exhibitor'):
                return JsonResponse({'error': 'Permission denied!'}, status=403)
            form = ResApplicationForm(request.POST, request.FILES)
            if not form.is_valid():
                first_error_key, first_error_messages = list(form.errors.items())[0]
                first_error_message = first_error_key + ': ' + first_error_messages[0]
                return JsonResponse({'error': first_error_message}, status=400)
            booth_id = form.cleaned_data.get('booth_id')
            category = form.cleaned_data.get('category')
            quantity = form.cleaned_data.get('quantity')
            content = form.cleaned_data.get('message_content')

            # 创建新的ResourceApplication和Message
            booth = Booth.objects.get(pk=booth_id)
            new_res_application = ResourceApplication.objects.create(applicant=request.user, booth=booth,
                                                                     category=category, quantity=quantity)
            new_res_application.save()
            # 创建提示消息和消息详情
            new_message = Message.objects.create(title='New Resource Application for ' + category.name,
                                                 sender=request.user, recipient=Manager.objects.first().detail)
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

