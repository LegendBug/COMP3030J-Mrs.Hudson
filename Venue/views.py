from django.shortcuts import render, redirect


def home(request):
    if not request.user.is_authenticated:
        return redirect('User:login')
    return render(request, 'Venue/home.html')