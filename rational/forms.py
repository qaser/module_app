from django import forms
from django.forms import ModelForm, ModelChoiceField, Textarea, Select
from .models import Proposal, Equipment, ModuleUser
from django.core.exceptions import ValidationError


class IndentedModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        # Добавляем отступы в зависимости от уровня иерархии
        return f"{'...' * obj.level} {obj.name}"


class ProposalForm(ModelForm):
    equipment = IndentedModelChoiceField(queryset=Equipment.objects.none(), label='Структурное подразделение')

    class Meta:
        model = Proposal
        fields = (
            'title',
            'authors',
            'equipment',
            'category',
            'economy_size',
            'description',
            'note',
        )
        widgets = {
            'description': Textarea(attrs={'rows': 20}),
            'title': Textarea(attrs={'rows': 3}),
            'note': Textarea(attrs={'rows': 4}),
            'authors': Select(attrs={'multiple': False}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Получаем текущего пользователя
        super().__init__(*args, **kwargs)

        if user:
            if user.role == 'employee':
                equipment_queryset = user.equipment.get_descendants(include_self=True).filter(
                    structure='Административная структура'
                )
                authors_queryset = ModuleUser.objects.filter(equipment__in=equipment_queryset)
            elif user.role == 'manager':
                if user.equipment.level > 1:
                    second_level_ancestor = user.equipment.get_ancestors().filter(level=1).first()
                else:
                    second_level_ancestor = user.equipment if user.equipment.level == 1 else None
                if second_level_ancestor:
                    descendants = second_level_ancestor.get_descendants(include_self=True)
                    equipment_queryset = descendants.filter(structure="Административная структура")
                else:
                    equipment_queryset = Equipment.objects.none()
                authors_queryset = ModuleUser.objects.filter(equipment__in=equipment_queryset)
                authors_queryset = ModuleUser.objects.filter(equipment__in=equipment_queryset)
            elif user.role == 'admin':
                equipment_queryset = Equipment.objects.filter(structure='Административная структура')
                authors_queryset = ModuleUser.objects.all()

            # Применяем queryset для полей authors и equipment
            self.fields['authors'].queryset = authors_queryset.order_by('last_name', 'first_name')
            self.fields['equipment'].queryset = equipment_queryset

            # Устанавливаем начальные значения
            self.fields['authors'].initial = user.id
            self.fields['equipment'].initial = user.equipment

    def clean(self):
        cleaned_data = super().clean()
        # Проверка полей authors
        authors_fields = [cleaned_data.get(f'authors_{i}') for i in range(1, 5)]
        filled_authors = [author for author in authors_fields if author]
        if len(filled_authors) == 0:
            raise ValidationError("Необходимо указать хотя бы одного автора.")
        # Устанавливаем значение is_economy
        economy_size = cleaned_data.get('economy_size', 0)
        if economy_size != 0:
            cleaned_data['is_economy'] = True
        else:
            cleaned_data['is_economy'] = False
        return cleaned_data
