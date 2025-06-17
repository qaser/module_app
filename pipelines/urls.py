from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views


app_name = 'pipelines'

urlpatterns = [
    path('', views.single_pipeline, name='index'),
]
