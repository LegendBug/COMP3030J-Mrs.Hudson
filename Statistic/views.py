from django.shortcuts import render







def statistic(request):
    user_type = 'Manager' if hasattr(request.user, 'manager') \
        else 'Organizer' if hasattr(request.user, 'organizer') \
        else 'Exhibitor' if hasattr(request.user, 'exhibitor') \
        else 'Guest'

    return render(request, 'Statistic/statistic.html', {'user_type': user_type})
