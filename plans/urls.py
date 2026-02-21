from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views


app_name = 'plans'

urlpatterns = [
    path('', views.index, name='index'),

    path('reports/', login_required(views.ReportsView.as_view()), name='reports'),
    path('reports/events/', views.document_events, {'doc_type': 'report'}, name='reports-events'),
    path('reports/<int:doc_id>/', views.single_document, {'doc_type': 'report'}, name='single_report'),

    path('protocols/', login_required(views.ProtocolsView.as_view()), name='protocols'),
    path('protocols/events/', views.document_events, {'doc_type': 'protocol'}, name='protocols-events'),
    path('protocols/<int:doc_id>/', views.single_document, {'doc_type': 'protocol'}, name='single_protocol'),

    path('orders/', login_required(views.OrdersView.as_view()), name='orders'),
    path('orders/events/', views.document_events, {'doc_type': 'order'}, name='orders-events'),
    path('orders/<int:doc_id>/', views.single_document, {'doc_type': 'order'}, name='single_order'),

    path('inspects/', login_required(views.InspectsView.as_view()), name='inspects'),
    path('inspects/events/', views.document_events, {'doc_type': 'inspect'}, name='inspects-events'),
    path('inspects/<int:doc_id>/', views.single_document, {'doc_type': 'inspect'}, name='single_inspect'),
]
