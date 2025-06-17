from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from equipments.models import Equipment
from users.models import Role

from .models import Pipeline


@login_required
def single_pipeline(request):
    pipeline = Pipeline.objects.all()
    return render(
        request,
        'pipelines/index.html',
    )
