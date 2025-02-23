import datetime as dt

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from locations.models import Location
from users.models import Role

from .filters import ValveFilter
from .forms import ValveForm
from .models import Service, Valve, ValveImage
from .tables import ValveTable


class ValveView(SingleTableMixin, FilterView):
    model = Valve
    table_class = ValveTable
    paginate_by = 39
    template_name = 'tpa/index.html'
    filterset_class = ValveFilter

    def get_queryset(self):
        if (self.request.user.profile.role != Role.ADMIN and self.request.user.profile.role != Role.MANAGER):
            station = self.request.user.profile.station
            queryset = Valve.objects.all().filter(location__department__station=station)
        else:
            queryset = Valve.objects.all()
        return queryset

    def get_table_kwargs(self):
       return {'request': self.request}


@login_required
def single_valve(request, valve_id):
    valve = Valve.objects.filter(id=valve_id)
    # print(valve.model._meta.fields)
    return render(
        request,
        'tpa/single-valve.html',
        {'valve_id': valve_id, 'valve': valve.model._meta.fields}
    )


@login_required
def valve_new(request):
    form = ValveForm(request.POST or None, user=request.user)
    if form.is_valid():
        valve = form.save()
        return redirect('tpa:single_valve', valve.id)
    return render(
        request,
        'tpa/form-tpa.html',
        {'form': form,}
    )


@login_required
def single_valve_service(request, valve_id):
    valve = get_object_or_404(Valve, id=valve_id)
    services_queryset = Service.objects.filter(valve=valve)
    current_year = dt.datetime.now().year
    years = [s.prod_year for s in services_queryset]
    if current_year not in years:
        years.append(current_year)
    years = set(years)
    services = {}
    for y in sorted(years):
        services[y] = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [], 11: [], 12: []}
    for s in services_queryset:
        services[s.prod_year][s.prod_month].append(s)
    return render(
        request,
        'tpa/single-valve-service.html',
        {'valve': valve, 'services': services}
    )


@login_required
def location_valve_service(request, loc_id):
    location = get_object_or_404(Location, id=loc_id)
    valves_queryset = Valve.objects.filter(location=location)
    # valves = []
    # services_queryset = Service.objects.filter(valve=valve)
    current_year = dt.datetime.now().year
    valve_nums = [v.tech_number for v in valves_queryset]
    # if current_year not in years:
    #     years.append(current_year)
    # years = set(years)
    services = {}
    valve_nums.sort()
    for num in valve_nums:
        services[num] = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [], 11: [], 12: []}
    for valve in valves_queryset:
        services_queryset = Service.objects.filter(valve=valve)
        for s in services_queryset:
            if s.prod_year == current_year:
                services[valve.tech_number][s.prod_month].append(s)
        # valves.append({'valve': valve, 'services': services})
    return render(
        request,
        'tpa/location-valve-service.html',
        {'location': location, 'services': services}
    )
