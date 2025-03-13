from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField, ModelForm, Select, Textarea

from .models import AnnualPlan, Equipment, ModuleUser, Proposal


class IndentedModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        # Добавляем отступы в зависимости от уровня иерархии
        return f"{'...' * obj.level} {obj.name}"


class ProposalForm(ModelForm):
    equipment = IndentedModelChoiceField(queryset=Equipment.objects.none(), label='Структурное подразделение')
    author_1 = ModelChoiceField(queryset=ModuleUser.objects.none(), label='Автор 1', required=False)
    author_2 = ModelChoiceField(queryset=ModuleUser.objects.none(), label='Автор 2', required=False)
    author_3 = ModelChoiceField(queryset=ModuleUser.objects.none(), label='Автор 3', required=False)
    author_4 = ModelChoiceField(queryset=ModuleUser.objects.none(), label='Автор 4', required=False)

    class Meta:
        model = Proposal
        fields = (
            'title',
            'equipment',
            'category',
            'economy_size',
            'is_economy',
            'description',
            'note',
        )
        widgets = {
            'description': Textarea(attrs={'rows': 20}),
            'title': Textarea(attrs={'rows': 3}),
            'note': Textarea(attrs={'rows': 4}),
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
            elif user.role == 'admin':
                equipment_queryset = Equipment.objects.filter(structure='Административная структура')
                authors_queryset = ModuleUser.objects.all()
            self.fields['author_1'].queryset = authors_queryset.order_by('last_name', 'first_name')
            self.fields['author_2'].queryset = authors_queryset.order_by('last_name', 'first_name')
            self.fields['author_3'].queryset = authors_queryset.order_by('last_name', 'first_name')
            self.fields['author_4'].queryset = authors_queryset.order_by('last_name', 'first_name')
            self.fields['equipment'].queryset = equipment_queryset
            self.fields['author_1'].initial = user.id
            self.fields['equipment'].initial = user.equipment

    def clean(self):
        cleaned_data = super().clean()
        authors = [
            cleaned_data.get('author_1'),
            cleaned_data.get('author_2'),
            cleaned_data.get('author_3'),
            cleaned_data.get('author_4'),
        ]
        authors = [author for author in authors if author]
        unique_authors = list(set(authors))
        if not unique_authors:
            raise ValidationError("Необходимо выбрать хотя бы одного автора.")
        cleaned_data['authors'] = unique_authors
        economy_size = cleaned_data.get('economy_size', 0)
        cleaned_data['is_economy'] = economy_size != 0
        return cleaned_data
