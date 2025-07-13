from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def user_cabinet(request):
    return render(request, 'users/cabinet.html')
