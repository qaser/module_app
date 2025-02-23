import datetime as dt

from django.forms import ChoiceField, FileField, ImageField, ModelForm
from django.forms.widgets import ClearableFileInput, NumberInput, Textarea

from leaks.models import Leak, LeakImage

from .utils import create_choices


class ImageWidget(ClearableFileInput):
    template_name = 'leaks/leaks_ext/form_extend/image_widget.html'


class LeakForm(ModelForm):
    # images = ImageField()
    images = FileField(widget=ClearableFileInput(attrs={'multiple': True}))
    # title = ChoiceField(
    #     choices=create_choices(Leak.objects.values_list('title', flat=True).distinct().order_by('title')),
    #     label='Наименование ТПА'
    # )
    # design = ChoiceField(
    #     choices=create_choices(Valve.objects.values_list('design', flat=True).distinct().order_by('design')),
    #     label='Исполнение'
    # )

    class Meta:
        model = Leak
        fields = (
            'direction',
            'place',
            'location',
            'is_valve',
            'specified_location',
            'description',
            'type_leak',
            'volume',
            'volume_dinamic',
            'gas_losses',
            'reason',
            'detection_date',
            'planned_date',
            'fact_date',
            'method',
            'detector',
            'executor',
            'plan_work',
            'doc_name',
            'protocol',
            'is_done',
            'note',
            'is_draft',
        )
        widgets = {
            'description': Textarea(attrs={'rows': 4}),
            'images': ImageWidget(),
        }