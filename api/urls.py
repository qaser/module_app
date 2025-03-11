from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('leaks', views.LeaksViewSet, basename='leaks')
router.register('users', views.UserViewSet, basename='users')
router.register('valves', views.ValveViewSet, basename='valves')
router.register('valve-images', views.ValveImageViewSet, basename='valve-images')
router.register('valve-docs', views.ValveDocumentViewSet, basename='valve-docs')
router.register('services', views.ServiceViewSet, basename='services')
router.register('service-types', views.ServiceTypeViewSet, basename='service-types')
router.register('works', views.WorkServiceView, basename='works')
router.register('factories', views.FactoryViewSet, basename='factories')
router.register('rational', views.ProposalViewSet, basename='rational')
router.register('rational-docs', views.ProposalDocumentViewSet, basename='rational-docs')
router.register(r'equipment-search', views.EquipmentViewSet, basename='equipment-search')
router.register('statuses', views.StatusViewSet, basename='statuses')
router.register(r'valves/(?P<valve_id>\d+)/services', views.ValveServiceViewSet, basename='valve-services')
router.register(r'plans', views.PlanViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
