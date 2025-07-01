from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'app_name', 'is_read', 'created_at')
    list_filter = ('app_name', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    readonly_fields = ('created_at',)
    list_editable = ('is_read',)
    date_hierarchy = 'created_at'
