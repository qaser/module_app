from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views.equipments_views import DepartmentViewSet, EquipmentViewSet
from api.views.leaks_views import LeaksViewSet
from api.views.notifications_views import NotificationViewSet
from api.views.pipelines_views import (DiagnosticDocumentViewSet,
                                       DiagnosticsViewSet, NodeStatesViewSet,
                                       PipeDocumentViewSet, PipeLimitViewSet,
                                       PipelineViewSet, PipeStatesViewSet,
                                       PipeViewSet, TubesViewSet,
                                       TubeVersionDocumentViewSet)
from api.views.rational_views import (
    AnnualPlanViewSet, ProposalDocumentViewSet, ProposalViewSet,
    QuarterlyPlanViewSet, StatusViewSet)
from api.views.tpa_views import (FactoryViewSet, ServiceTypeViewSet,
                                 ServiceViewSet, ValveDocumentViewSet,
                                 ValveImageViewSet, ValveServiceViewSet,
                                 ValveViewSet, WorkServiceView)
from api.views.users_views import UserViewSet

router = DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register('notifications', NotificationViewSet, basename='notification')

router.register('equipment-search', EquipmentViewSet, basename='equipment-search')
router.register('department-search', DepartmentViewSet, basename='department-search')

router.register('leaks', LeaksViewSet, basename='leaks')

router.register('valves', ValveViewSet, basename='valves')
router.register('valve-images', ValveImageViewSet, basename='valve-images')
router.register('valve-docs', ValveDocumentViewSet, basename='valve-docs')
router.register('services', ServiceViewSet, basename='services')
router.register('service-types', ServiceTypeViewSet, basename='service-types')
router.register('works', WorkServiceView, basename='works')
router.register('factories', FactoryViewSet, basename='factories')
router.register(r'valves/(?P<valve_id>\d+)/services', ValveServiceViewSet, basename='valve-services')

router.register('rational', ProposalViewSet, basename='rational')
router.register('rational-docs', ProposalDocumentViewSet, basename='rational-docs')
router.register('statuses', StatusViewSet, basename='statuses')
router.register('rational-plans', AnnualPlanViewSet, basename='rational-plans')
router.register(r'rational-plans/(?P<plan_id>\d+)/quarterly', QuarterlyPlanViewSet, basename='rational-plans-quarterly')

router.register('pipelines', PipelineViewSet, basename='pipelines')
router.register('pipe-states', PipeStatesViewSet, basename='pipe-states')
router.register('node-states', NodeStatesViewSet, basename='node-states')
router.register('pipes', PipeViewSet, basename='pipes')
router.register('pipe-limits', PipeLimitViewSet, basename='pipe-limits')
router.register('pipe-docs', PipeDocumentViewSet, basename='pipe-docs')
router.register(r'pipes/(?P<pipe_id>\d+)/tubes', TubesViewSet, basename='pipe_tubes')
router.register('tubes', TubesViewSet, basename='tubes')
router.register('tube-docs', TubeVersionDocumentViewSet, basename='tube-docs')
router.register('diagnostics', DiagnosticsViewSet, basename='diagnostics')
router.register('diagnostic-docs', DiagnosticDocumentViewSet, basename='diagnostic-docs')


urlpatterns = [
    path('', include(router.urls)),
]
