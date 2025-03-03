import datetime as dt

from django.forms import (
    ChoiceField, FileField, ImageField, ModelChoiceField, ModelForm)
from django.forms.widgets import ClearableFileInput, NumberInput, Textarea

from equipments.models import Equipment
from module_app.utils import create_choices
from users.models import ModuleUser, Role

from .models import Proposal


class ProposalForm(ModelForm):
    pass
    # equipment = ModelChoiceField(queryset=Equipment.objects.none(), label='Место нахождения')

    # class Meta:
    #     model = Proposal
    #     fields = (
    #         'equipment',
    #         'title',
    #         'diameter',
    #         'pressure',
    #         'valve_type',
    #         'factory',
    #         'year_made',
    #         'year_exploit',
    #         'tech_number',
    #         'factory_number',
    #         'inventory_number',
    #         'lifetime',
    #         'remote',
    #         'label',
    #         'design',
    #         'material',
    #         'drive_type',
    #         'drive_factory',
    #         'drive_year_exploit',
    #         'description',
    #     )
    #     widgets = {
    #         'description': Textarea(attrs={'rows': 4}),
    #     }

    # def __init__(self, *args, **kwargs):
    #     user = kwargs.pop('user', None)  # Получаем пользователя из kwargs
    #     super(ProposalForm, self).__init__(*args, **kwargs)
    #     if user:
    #         base_level = 0  # Базовый уровень для отступов
    #         if user.role == Role.ADMIN:
    #             # ADMIN может выбирать всё оборудование
    #             self.fields['equipment'].queryset = Equipment.objects.all()
    #         elif user.role == Role.MANAGER:
    #             # MANAGER может выбирать оборудование своей ветки, начиная со второго уровня
    #             if user.equipment:
    #                 root = user.equipment.get_root()  # Получаем корень ветки
    #                 descendants = root.get_descendants(include_self=True)  # Вся ветка
    #                 # Фильтруем оборудование, начиная со второго уровня
    #                 self.fields['equipment'].queryset = descendants.filter(level__gte=1)
    #                 base_level = 1  # Базовый уровень — второй уровень
    #             else:
    #                 self.fields['equipment'].queryset = Equipment.objects.none()
    #         elif user.role == Role.EMPLOYEE:
    #             # EMPLOYEE может выбирать оборудование своей ветки, начиная с уровня своего оборудования
    #             if user.equipment:
    #                 descendants = user.equipment.get_descendants(include_self=True)  # Вся ветка
    #                 self.fields['equipment'].queryset = descendants
    #                 base_level = user.equipment.level  # Базовый уровень — уровень оборудования пользователя
    #             else:
    #                 self.fields['equipment'].queryset = Equipment.objects.none()
    #         else:
    #             self.fields['equipment'].queryset = Equipment.objects.none()
    #         # Добавляем отступы для отображения иерархии
    #         self.fields['equipment'].label_from_instance = lambda obj: f"{'..' * (obj.level - base_level)} {obj.name}"
