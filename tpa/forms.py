import datetime as dt

from django.forms import ChoiceField, FileField, ImageField, ModelForm, ModelChoiceField
from django.forms.widgets import ClearableFileInput, NumberInput, Textarea

from users.models import User, Role, Profile
from tpa.models import Valve, ValveImage
from locations.models import Location, Department, Direction, TypeOfLocation, Station

from .utils import create_choices


class ValveForm(ModelForm):
    # direction = ChoiceField(label='Филиал', choices=[], required=True)
    # station = ChoiceField(label='КС', choices=[], required=True)
    # department = ChoiceField(label='Служба', choices=[], required=True)
    location = ModelChoiceField(queryset=Location.objects.none(), label="Оборудование")

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and hasattr(user, 'profile') and user.profile.station:
            # Фильтруем Location только для станций пользователя
            self.fields['location'].queryset = Location.objects.filter(department__station=user.profile.station)

    class Meta:
        model = Valve
        fields = (
            # 'direction',
            # 'station',
            # 'department',
            'location',
            'title',
            'diameter',
            'pressure',
            'valve_type',
            'factory',
            'year_made',
            'year_exploit',
            'tech_number',
            'factory_number',
            'inventory_number',
            'lifetime',
            'remote',
            'label',
            'design',
            'material',
            'drive_type',
            'drive_factory',
            'drive_year_exploit',
            'description',
        )
        widgets = {
            'description': Textarea(attrs={'rows': 4}),
        }
