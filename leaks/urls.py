from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

app_name = 'leaks'

urlpatterns = [
    path('', login_required(views.LeakView.as_view()), name='index'),
    path('<int:leak_id>/', views.single_leak, name='single_leak'),
    path('leaks/new/', views.leak_new, name='leak_new'),
    # path('leak-edit/<int:leak_id>/', views.leak_edit, name='leak_edit'),
    # path('<int:valve_id>/service/', views.single_valve_service, name='single_valve_service'),
    # path('<int:loc_id>/location-valve-service/', views.location_valve_service, name='location_valve_service'),
    # path('', views.index, name='index'),
    # path('<slug:slug>/', views.index_apk, name='index_control'),
    # path('<slug:slug>/acts/new/', views.act_new, name='act_new'),
]
