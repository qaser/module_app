from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

app_name = 'pipelines'

urlpatterns = [
    path('', views.scheme_pipelines, name='index'),
    path('repairs/', login_required(views.RepairsView.as_view()), name='repairs'),
    path('diagnostics/', login_required(views.DiagnosticsView.as_view()), name='diagnostics'),
    # path('plans/', login_required(views.PlansView.as_view()), name='plans'),
    path('plans/', views.scheme_pipelines, name='plans'),
    path('pipes/<int:pipe_id>/', views.single_pipe, name='single_pipe'),
    path('pipes/<int:pipe_id>/tubes/', login_required(views.TubesView.as_view()), name='pipe-tubes'),
    path('pipes/<int:pipe_id>/tubes/<int:tube_id>/', views.single_tube, name='single_tube'),
    # path('rapairs/<int:repair_id>/', views.single_repair, name='single_repair'),
]
