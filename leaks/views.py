from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from leaks.forms import LeakForm
from users.models import Role

# from .filters import LeakFilter
from .models import Leak, LeakImage
from .tables import LeakTable


class LeakView(SingleTableMixin, FilterView):
    model = Leak
    table_class = LeakTable
    paginate_by = 20
    template_name = 'leaks/index.html'
    # filterset_class = LeakFilter

    # def get_queryset(self):
    #     if (self.request.user.profile.role != Role.ADMIN and self.request.user.profile.role != Role.MANAGER):
    #         structure = self.request.user.structure
    #         queryset = Leak.objects.all().filter(location__department__station__direction=direction)
    #     else:
    #         queryset = Leak.objects.all()
    #     return queryset

    def get_table_kwargs(self):
       return {'request': self.request}


@login_required
def single_leak(request, leak_id):
    leak = Leak.objects.filter(id=leak_id)
    return render(
        request,
        'leaks/single-leak.html',
        {'leak_id': leak_id, 'leak': leak.model._meta.fields}
    )


@login_required
def leak_new(request):
    form = LeakForm(
        request.POST or None,
        files=request.FILES or None,
    )
    files = request.FILES.getlist('images')
    if form.is_valid():
        for f in files:
            LeakImage.objects.create(leak=form.instance, image=f)
            form.save()
        # return redirect('tpa:single_valve', leak_id)
        return redirect('leaks:single_leak')
    return render(request, 'leaks/form-leak.html', {'form': form}
    )
