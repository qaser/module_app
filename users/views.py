from django.shortcuts import render


def user_cabinet(request):
    return render(request, 'users/cabinet.html')
