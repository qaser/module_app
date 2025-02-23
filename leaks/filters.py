import django_filters as df

from locations.models import Direction, Location
from users.models import Role

from .models import Leak
from .utils import create_choices


class LeakFilter(df.FilterSet):
    direction = df.ModelChoiceFilter(
        field_name='location__department__station__direction',
        label='Структурное подразделение',
        queryset=Direction.objects.all()
    )
    location = df.ChoiceFilter(
        field_name='location__name',
        label='Наименование объекта',
        choices=create_choices(
            Location.objects.values_list('name', flat=True).distinct().order_by('name')
        ),
    )
    place = df.ChoiceFilter(
        choices=create_choices(
            Leak.objects.values_list('place', flat=True).distinct().order_by('place')
        )
    )
    is_done = df.ChoiceFilter(
        choices=create_choices(
            Leak.objects.values_list('is_done', flat=True).distinct().order_by('is_done')
        )
    )


    def __init__(self, *args, **kwargs):
        user = kwargs['request'].user
        super(LeakFilter, self).__init__(*args, **kwargs)
        if (user.profile.role != Role.ADMIN and user.profile.role != Role.MANAGER):
            self.filters.pop('direction')


    class Meta:
        model = Leak
        fields = [
            'direction',
            'location',
            'place',
            'is_done',
        ]
