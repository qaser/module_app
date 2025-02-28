import csv

from django.core.management import BaseCommand

from equipments.models import Department, Direction, Location, Station
from tpa.models import Factory, Valve, ValveImage


class Command(BaseCommand):
    help = 'Update database'

    def handle(self, *args, **options):
        with open('csv/valve.csv', encoding='utf-8') as file:
            reader = file.readlines()
            for i, row in enumerate(reader):
                dir, ks_dep, loc, title, dia, pres, v_type, fac, y_made, y_exp, t_num, f_num, i_num, life, remote, label, mat, design, d_type, d_fac, d_y_exp, desc = row.split(';')
                if i:
                    lifetime = None if life == '' else life
                    lpu, mg, dir_name  = dir.split()
                    direction, _ = Direction.objects.get_or_create(name=f'{dir_name} {lpu}{mg}')
                    ks, dep  = ks_dep.split(',')
                    station, _ = Station.objects.get_or_create(name=ks, direction=direction)
                    department, _ = Department.objects.get_or_create(name=dep.lstrip(), station=station)
                    location, _ = Location.objects.get_or_create(name=loc, department=department)
                    fac_name = fac.split(',')[0]
                    fac_country = fac.split(',')[1]
                    factory, _ = Factory.objects.get_or_create(name=fac_name, country=fac_country.lstrip())
                    title = title.capitalize()
                    if d_type != 'без привода':
                        drive_fac_name = d_fac.split(',')[0]
                        drive_fac_country = d_fac.split(',')[1]
                        drive_factory, _ = Factory.objects.get_or_create(
                            name=drive_fac_name,
                            country=drive_fac_country.lstrip()
                        )
                        drive_year_exploit=int(d_y_exp)
                    else:
                        drive_factory=None
                        drive_year_exploit=None
                    Valve.objects.get_or_create(
                        location=location,
                        title=title,
                        diameter=dia,
                        pressure=pres,
                        valve_type=v_type,
                        factory=factory,
                        year_made=y_made,
                        year_exploit=y_exp,
                        tech_number=t_num,
                        factory_number=f_num,
                        inventory_number=i_num,
                        lifetime=lifetime,
                        remote=remote,
                        label=label,
                        material=mat,
                        design=design,
                        drive_type=d_type,
                        drive_factory=drive_factory,
                        drive_year_exploit=drive_year_exploit,
                        description=desc
                    )
