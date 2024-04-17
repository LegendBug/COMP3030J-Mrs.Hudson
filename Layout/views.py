from django.shortcuts import render

def venue_layout(request):
    return render(request, 'Layout/venue_layout.html')
