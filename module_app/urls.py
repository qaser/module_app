from django.conf.urls import handler400, handler404, handler500, include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from module_app import settings

handler404 = 'module_app.views.page_not_found'  # noqa
handler500 = 'module_app.views.server_error'  # noqa
handler400 = 'module_app.views.bad_request'  # noqa

urlpatterns = [
    path('app-admin/', admin.site.urls),
    path('leaks/', include('leaks.urls')),
    path('pipelines/', include('pipelines.urls')),
    path('tpa/', include('tpa.urls')),
    path('rational/', include('rational.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
