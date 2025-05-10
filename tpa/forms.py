from django.forms import ModelChoiceField, ModelForm
from django.forms.widgets import Textarea

from equipments.models import Equipment
from tpa.models import Valve
from users.models import Role


class ValveForm(ModelForm):
    equipment = ModelChoiceField(queryset=Equipment.objects.none(), label='Место нахождения')

    class Meta:
        model = Valve
        fields = (
            'equipment',
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
            'note',
        )
        widgets = {
            'note': Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Получаем пользователя из kwargs
        super(ValveForm, self).__init__(*args, **kwargs)
        if user:
            if user.role == Role.ADMIN:
                # ADMIN может выбирать всё оборудование
                self.fields['equipment'].queryset = Equipment.objects.all()
            elif user.role == Role.MANAGER:
                # MANAGER может выбирать оборудование своей ветки, начиная со второго уровня
                if user.department:
                    root = user.department.get_root()  # Получаем корень ветки
                    departments = root.get_descendants(include_self=True)
                    self.fields['equipment'].queryset = Equipment.objects.filter(departments__in=departments)
                else:
                    self.fields['equipment'].queryset = Equipment.objects.none()
            elif user.role == Role.EMPLOYEE:
                # EMPLOYEE может выбирать оборудование своей ветки, начиная с уровня своего оборудования
                if user.department:
                    departments = user.department.get_descendants(include_self=True)  # Вся ветка
                    self.fields['equipment'].queryset = Equipment.objects.filter(departments__in=departments)
                else:
                    self.fields['equipment'].queryset = Equipment.objects.none()
            else:
                self.fields['equipment'].queryset = Equipment.objects.none()

        def label_from_instance(obj):
            ancestors = obj.get_ancestors()
            indent = '..' * len(ancestors)
            return f"{indent} {obj.name}" if indent else obj.name

        self.fields['equipment'].label_from_instance = label_from_instance
