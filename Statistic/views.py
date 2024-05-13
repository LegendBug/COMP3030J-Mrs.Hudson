from django.http import JsonResponse
from django.shortcuts import render
from Inventory.views import get_all_venues_monthly_consumption


def get_consumption_data(request, year):
    # 获取整合了用水量和用电量的统计数据
    combined_statistics = get_all_venues_monthly_consumption(year)

    # 分别存储用水量和用电量的数据字典
    water_statistics = {}
    electric_statistics = {}

    for month_data in combined_statistics:
        month_num = month_data[0]
        formatted_month = f"Month {month_num}"
        total_water = month_data[1]['total_water']
        total_power = month_data[1]['total_power']

        # 将用水量和用电量数据分别存储在对应的字典中
        water_statistics[formatted_month] = total_water
        electric_statistics[formatted_month] = total_power
    # water_statistics = {
    #     "Month 1": 1200,
    #     "Month 2": 1600,
    #     "Month 3": 1000,
    #     "Month 4": 800,
    #     "Month 5": 900,
    #     "Month 6": 1600,
    #     "Month 7": 2100,
    #     "Month 8": 2200,
    #     "Month 9": 1800,
    #     "Month 10": 1500,
    #     "Month 11": 1300,
    #     "Month 12": 900,
    # }
    #
    # # 生成用电量的假数据
    # electric_statistics = {
    #     "Month 1": 100,
    #     "Month 2": 1600,
    #     "Month 3": 1000,
    #     "Month 4": 800,
    #     "Month 5": 900,
    #     "Month 6": 1600,
    #     "Month 7": 210,
    #     "Month 8": 2200,
    #     "Month 9": 1800,
    #     "Month 10": 150,
    #     "Month 11": 1300,
    #     "Month 12": 900,
    # }

    # 返回用水量和用电量的数据字典
    return JsonResponse({'water_statistics': water_statistics, 'electric_statistics': electric_statistics})


def statistic(request):
    user_type = 'Manager' if hasattr(request.user, 'manager') \
        else 'Organizer' if hasattr(request.user, 'organizer') \
        else 'Exhibitor' if hasattr(request.user, 'exhibitor') \
        else 'Guest'
    return render(request, 'Statistic/statistic.html', {'user_type': user_type})
