from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

app_name = 'pipelines'

urlpatterns = [
    path('', views.scheme_pipelines, name='index'),
    path('repairs/', login_required(views.RepairsView.as_view()), name='repairs'),
    path('diagnostics/', login_required(views.DiagnosticsView.as_view()), name='diagnostics'),
    path('diagnostics/<int:diagnostic_id>/', views.single_diagnostic, name='single_diagnostic'),
    path(
        'diagnostics/<int:diagnostic_id>/tubes/',
        login_required(views.DiagnosticTubesView.as_view()),
        name='diagnostic_tubes'
    ),
    # path(
    #     'diagnostics/<int:diagnostic_id>/tube-units/',
    #     login_required(views.DiagnosticTubeUnitsView.as_view()),
    #     name='diagnostic_tube_units'
    # ),
    # path('diagnostics/<int:diagnostic_id>/bends/', views.diagnostic_bends, name='diagnostic_bends'),
    # path('diagnostics/<int:diagnostic_id>/anomalies/', views.diagnostic_anomalies, name='diagnostic_anomalies'),
    # path('diagnostics/<int:diagnostic_id>/defects/', views.diagnostic_defects, name='diagnostic_defects'),
    # path('plans/', login_required(views.PlansView.as_view()), name='plans'),
    path('plans/', views.scheme_pipelines, name='plans'),
    path('pipes/<int:pipe_id>/', views.single_pipe, name='single_pipe'),
    path('pipes/<int:pipe_id>/tubes/', login_required(views.TubesView.as_view()), name='pipe-tubes'),
    path('pipes/<int:pipe_id>/tubes/<int:tube_id>/', views.single_tube, name='single_tube'),
    # path('rapairs/<int:repair_id>/', views.single_repair, name='single_repair'),
]
