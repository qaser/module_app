import django_filters as df

from locations.models import Department, Direction, Location, Station
from users.models import Role

from .models import Valve
from .utils import create_choices


class ValveFilter(df.FilterSet):
    station = df.ModelChoiceFilter(
        field_name='location__department__station',
        label='КС',
        queryset=Station.objects.all()
    )
    department = df.ModelChoiceFilter(
        field_name='location__department',
        label='Служба филиала',
        queryset=Department.objects.all()
    )
    location = df.ChoiceFilter(
        field_name='location__name',
        label='Место установки',
        choices=create_choices(
            Location.objects.values_list('name', flat=True).distinct().order_by('name')
        ),
    )
    title = df.ChoiceFilter(
        choices=create_choices(
            Valve.objects.values_list('title', flat=True).distinct().order_by('title')
        )
    )
    diameter = df.ChoiceFilter(
        choices=create_choices(
            Valve.objects.values_list('diameter', flat=True).distinct().order_by('diameter')
        )
    )
    pressure = df.ChoiceFilter(
        choices=create_choices(
            Valve.objects.values_list('pressure', flat=True).distinct().order_by('pressure')
        )
    )
    tech_number = df.ChoiceFilter(
        choices=create_choices(
            Valve.objects.values_list('tech_number', flat=True).distinct().order_by('tech_number')
        )
    )

    def __init__(self, *args, **kwargs):
        user = kwargs['request'].user
        super(ValveFilter, self).__init__(*args, **kwargs)
        if (user.profile.role != Role.ADMIN and user.profile.role != Role.MANAGER):
            self.filters.pop('station')


    class Meta:
        model = Valve
        fields = [
            'station',
            'department',
            'location',
            'title',
            'diameter',
            'pressure',
            'valve_type',
            'factory',
            'tech_number',
            'drive_type'
        ]
