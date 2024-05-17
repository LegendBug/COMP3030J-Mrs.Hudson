import json
from django.shortcuts import render
from rest_framework import status
from Booth.models import Booth
from Exhibition.models import Exhibition
from Venue.models import Venue
from django.http import JsonResponse
from .forms import AddLayerForm, EditLayerForm
from .serializers import *
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view


def venue_layout(request):
    user_type = 'Manager' if hasattr(request.user, 'manager') \
        else 'Organizer' if hasattr(request.user, 'organizer') \
        else 'Exhibitor' if hasattr(request.user, 'exhibitor') \
        else 'Guest'
    # 从session中获取venue_id
    venue_id = request.session.get('venue_id')
    venue = Venue.objects.get(id=venue_id)
    # 获取当前场馆的items
    items = venue.items.all()
    # add_layer_form
    add_sublayer_form = AddLayerForm(initial={'parent_id': 1, 'floor': venue.floor})
    return render(request, 'Layout/venue_layout.html',
                  {'venue': venue, 'items': items, 'user_type': user_type, 'floor_range': range(1, venue.floor),
                   'add_sublayer_form': add_sublayer_form})


def layout(request):
    # 从session中获取venue_id
    venue_id = request.session.get('venue_id')
    venue = Venue.objects.get(id=venue_id)
    user_type = 'Manager' if hasattr(request.user, 'manager') \
        else 'Organizer' if hasattr(request.user, 'organizer') \
        else 'Exhibitor' if hasattr(request.user, 'exhibitor') \
        else 'Guest'
    # 获取当前场馆的items
    items = venue.items.all()
    # add_layer_form
    add_sublayer_form = AddLayerForm(initial={'parent_id': 1, 'floor': venue.floor})
    edit_layer_form = EditLayerForm()
    return render(request, 'Layout/layout.html',
                  {'current_access': venue, 'user_type': user_type, 'items': items,
                   'floor_range': range(1, venue.floor + 1),
                   'add_sublayer_form': add_sublayer_form, 'edit_layer_form': edit_layer_form})


def refresh_data(request):
    if request.method == 'GET':
        # 从GET请求中获取参数
        floor = int(request.GET.get('floor', 1))
        current_access_id = int(request.GET.get('current_access_id', 0))
        user_type = request.GET.get('user_type')
        # 验证数据有效性
        if (floor < 1) or (current_access_id is None) or (user_type not in ['Manager', 'Organizer', 'Exhibitor']):
            return JsonResponse({'error': 'Invalid request'}, status=400)
        # 获取当前正在访问的位置
        if user_type == 'Manager':
            current_access = Venue.objects.get(pk=current_access_id)
        elif user_type == 'Organizer':
            current_access = Exhibition.objects.get(pk=current_access_id)
        else:
            current_access = Booth.objects.get(pk=current_access_id)
        # 获取当前场馆的当前楼层的Root SpaceUnit节点(parent_unit=None 且创建时间最早)
        root = current_access.sectors.filter(floor=floor, parent_unit=None).order_by('created_at').first()
        # 返回JSON化的root数据
        if root is not None:
            # 使用Serializer序列化root
            serializer = SpaceUnitSerializer(root)
            return JsonResponse(serializer.data)  # 使用Django的JsonResponse返回数据
        else:
            return JsonResponse({'error': 'No root SpaceUnit found for the specified floor'},
                                status=status.HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def add_sublayer(request):
    if request.method == 'POST':
        form = AddLayerForm(request.POST)
        if form.is_valid():
            form.save(commit=True)  # save the form and create the new sublayer
            return JsonResponse({'success': 'The new Sublayer has been successfully added!'}, status=200)
        else:
            return JsonResponse({'error': form.errors}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


def delete_layer(request):
    if request.method == 'GET':
        floor = int(request.GET.get('floor', 1))
        user_type = request.GET.get('user_type')
        current_access_id = int(request.GET.get('current_access_id', 0))
        # 验证数据有效性:
        if (floor < 1) or (current_access_id is None) or (user_type not in ['Manager', 'Organizer', 'Exhibitor']):
            return JsonResponse({'error': 'Invalid request'}, status=400)
        layer_id = int(request.GET.get('layer_id', 0))
        layer = get_object_or_404(SpaceUnit, id=layer_id)
        if user_type == 'Manager':
            current_access = get_object_or_404(Venue, pk=current_access_id)
        elif user_type == 'Organizer':
            current_access = get_object_or_404(Exhibition, pk=current_access_id)
        else:
            current_access = get_object_or_404(Booth, pk=current_access_id)
        root = current_access.sectors.filter(floor=floor, parent_unit=None).order_by('created_at').first()
        if root == layer:  # 表明当前SpaceUnit是根节点,不能删除
            return JsonResponse({'error': 'The root SpaceUnit cannot be deleted!'}, status=400)

        def recursively_delete(space_unit):
            # 先递归删除所有子单位
            for child in space_unit.child_units.all():
                recursively_delete(child)
            if not space_unit.available and not space_unit.occupied_units.exists():  # 表明当前SpaceUnit没有被预约使用
                # 删除与此SpaceUnit相关联的所有elements
                space_unit.elements.all().delete()
                # 最后删除SpaceUnit本身
                space_unit.delete()

        # 开始递归删除操作
        recursively_delete(layer)
        # 返回删除成功的信息
        return JsonResponse({'success': 'The unused Layer has been successfully deleted!'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def edit_layer(request):
    if request.method == 'POST':
        space_unit_id = request.POST.get('id')
        space_unit = get_object_or_404(SpaceUnit, id=space_unit_id)
        form = EditLayerForm(request.POST, instance=space_unit)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': 'The Layer has been successfully updated!'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def add_element(request):
    if request.method == 'POST':
        element_type = request.POST.get('type')
        name = request.POST.get('name')
        transformable = request.POST.get('transformable', 'true') == 'true'
        element_data = request.POST.get('data')
        layer_id = request.POST.get('layer_id')
        image_file = request.FILES.get('image')  # 获取上传的图片文件

        layer = get_object_or_404(SpaceUnit, id=layer_id)
        # 创建KonvaElement实例
        konva_element = KonvaElement.objects.create(
            name=name,
            layer=layer,
            type=element_type,
            data=element_data,
            transformable=transformable,
            image=image_file  # 将上传的图片文件保存到数据库
        )

        updated_element_data = json.loads(element_data)
        updated_element_data["attrs"]["id"] = f"{konva_element.pk}"  # 添加id属性
        konva_element.data = json.dumps(updated_element_data)  # 更新已创建的KonvaElement实例的data字段
        konva_element.save()

        # 返回新创建的KonvaElement的信息
        return JsonResponse({
            'id': konva_element.id,
            'name': konva_element.name,
            'layer': konva_element.layer.id if konva_element.layer else None,
            'type': konva_element.type,
            'data': konva_element.data,
            'image_url': konva_element.image.url if konva_element.image else None
        }, safe=False)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def edit_element(request): # {url (Layout:edit_element)}
    if request.method == 'POST':
        element_id = request.POST.get('id')
        name = request.POST.get('name')
        transformable = request.POST.get('transformable', 'true') == 'true'
        element_data = request.POST.get('data')
        image_file = request.FILES.get('image')  # 获取上传的图片文件

        konva_element = get_object_or_404(KonvaElement, id=element_id)
        # 更新KonvaElement实例
        konva_element.name = name
        konva_element.transformable = transformable
        konva_element.data = element_data
        if image_file:
            konva_element.image = image_file
        konva_element.save()

        # 返回新创建的KonvaElement的信息
        return JsonResponse({
            'id': konva_element.id,
            'name': konva_element.name,
            'layer': konva_element.layer.id if konva_element.layer else None,
            'type': konva_element.type,
            'data': konva_element.data,
            'image_url': konva_element.image.url if konva_element.image else None
        }, safe=False)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def delete_element(request):
    if request.method == 'GET':
        element_id = int(request.GET.get('element_id', 0))
        element = get_object_or_404(KonvaElement, id=element_id)
        element.delete()  # 删除元素
        return JsonResponse({'success': 'The element has been successfully deleted!'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def synchronize_elements_data(request): # 该方法与edit_element方法的区别是, 该方法只被用于Konva对象在画板上进行位移或变换后刷新Konva对象在后端的data属性中的数据
    if request.method == 'POST':
        data = json.loads(request.body)  # 使用 json.loads 解析请求体中的 JSON 数据
        root_data = data.get('root')
        if not root_data:
            return JsonResponse({'error': 'No root space unit provided.'}, status=400)

        def recursively_update(new_dic_data):  # 递归更新树结构的SpaceUnit其下的所有KonvaElement
            new_elements_dic_data = new_dic_data.get('elements')
            for i in range(len(new_elements_dic_data)):
                old_element = get_object_or_404(KonvaElement, id=int(new_elements_dic_data[i].get('id')))
                new_element_data = new_elements_dic_data[i]
                # 更新KonvaElement实例
                old_element.name = new_element_data.get('name')
                old_element.type = new_element_data.get('type')
                old_element.data = new_element_data.get('data')
                old_element.transformable = new_element_data.get('transformable')
                old_element.save()

            # 递归更新子SpaceUnit下的所有KonvaElement
            if (len(new_dic_data.get('child_units')) > 0):
                for i in range(len(new_dic_data.get('child_units'))):
                    if (len(new_dic_data.get('child_units')[i].get('elements')) > 0):
                        recursively_update(new_dic_data.get('child_units')[i])

        recursively_update(root_data)
        return JsonResponse({'success': 'The data has been successfully synchronized!'}, status=200)
    return JsonResponse({'error': 'Invalid request'}, status=400)
