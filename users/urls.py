from django.urls import path

from .views import user_cabinet


app_name = 'users'

urlpatterns = [
    path('', user_cabinet, name='main-menu'),
]
