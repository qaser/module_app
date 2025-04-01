from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField, ModelForm, Select, Textarea

from .models import ModuleUser, Proposal, Department


class IndentedModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        # Добавляем отступы в зависимости от уровня иерархии
        return f"{'...' * obj.level} {obj.name}"


class ProposalForm(ModelForm):
    department = IndentedModelChoiceField(queryset=Department.objects.none(), label='Структурное подразделение')
    author_1 = ModelChoiceField(queryset=ModuleUser.active_objects.none(), label='Автор 1', required=False)
    author_2 = ModelChoiceField(queryset=ModuleUser.active_objects.none(), label='Автор 2', required=False)
    author_3 = ModelChoiceField(queryset=ModuleUser.active_objects.none(), label='Автор 3', required=False)
    author_4 = ModelChoiceField(queryset=ModuleUser.active_objects.none(), label='Автор 4', required=False)

    class Meta:
        model = Proposal
        fields = (
            'title',
            'department',
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
                department_queryset = user.department.get_descendants(include_self=True)
                authors_queryset = ModuleUser.active_objects.filter(department__in=department_queryset)
            elif user.role == 'manager':
                if user.department.level > 1:
                    second_level_ancestor = user.department.get_ancestors().filter(level=1).first()
                else:
                    second_level_ancestor = user.department if user.department.level == 1 else None
                if second_level_ancestor:
                    department_queryset = second_level_ancestor.get_descendants(include_self=True)
                else:
                    department_queryset = Department.objects.none()
                authors_queryset = ModuleUser.active_objects.filter(department__in=department_queryset)
            elif user.role == 'admin':
                department_queryset = Department.objects.all()
                authors_queryset = ModuleUser.active_objects.all()
            self.fields['author_1'].queryset = authors_queryset.order_by('last_name', 'first_name')
            self.fields['author_2'].queryset = authors_queryset.order_by('last_name', 'first_name')
            self.fields['author_3'].queryset = authors_queryset.order_by('last_name', 'first_name')
            self.fields['author_4'].queryset = authors_queryset.order_by('last_name', 'first_name')
            self.fields['department'].queryset = department_queryset
            self.fields['author_1'].initial = user.id
            self.fields['department'].initial = user.department

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
