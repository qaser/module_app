from django.contrib import admin

from .models import Department, Direction, Location, Station, Structure, TypeOfLocation


class DirectionAdmin(admin.ModelAdmin):
    list_display = ('name',)


class StationAdmin(admin.ModelAdmin):
    list_display = ('name', 'direction',)


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'station', 'part_of')
    list_filter = (
        'part_of',
    )


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')


class TypeOfLocationAdmin(admin.ModelAdmin):
    list_display = ('name',)


class StructureAdmin(admin.ModelAdmin):
    list_display = ('structure_type',)


admin.site.register(Direction, DirectionAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(TypeOfLocation, TypeOfLocationAdmin)
admin.site.register(Structure, StructureAdmin)
