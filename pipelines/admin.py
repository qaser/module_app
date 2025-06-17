from django.contrib import admin
from .models import Pipeline


# Pipeline Admin
@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
