from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render

from Booth.models import Booth


@login_required
def booth(request, booth_id):
    current_booth = Booth.objects.filter(id=booth_id).first()
    if current_booth is None:
        exhibition_id = request.session.get('exhibition_id', None)
        if exhibition_id:
            return redirect('Exhibition:exhibition', exhibition_id=exhibition_id)
        else:
            return redirect('Venue:home')
    request.session['booth_id'] = booth_id  # 将booth_id存入session

    if request.method == 'GET':
        return render(request, 'Booth/booth.html', {'booth': current_booth})
    else:
        return HttpResponseNotAllowed(['GET'])