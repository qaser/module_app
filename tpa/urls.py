from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

app_name = 'tpa'

urlpatterns = [
    path('', login_required(views.ValveView.as_view()), name='index'),
    path('<int:valve_id>/', views.single_valve, name='single_valve'),
    path('valve-new/', views.valve_new, name='valve_new'),
    path('<int:valve_id>/service/', views.single_valve_service, name='single_valve_service'),
    path('<int:loc_id>/location-valve-service/', views.location_valve_service, name='location_valve_service'),
    # path('', views.index, name='index'),
    # path('<slug:slug>/', views.index_apk, name='index_control'),
    # path('<slug:slug>/acts/new/', views.act_new, name='act_new'),
]
