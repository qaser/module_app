import csv

from django.core.management import BaseCommand

from tpa.models import Factory


class Command(BaseCommand):
    help = 'Update database'

    def handle(self, *args, **options):
        with open('csv/factory.csv', encoding='utf-8') as file:
            reader = csv.reader(file)
            for i, row in enumerate(reader):
                if i and len(row) < 3 and len(row) > 0:
                    name, country = row
                    Factory.objects.get_or_create(
                        name=name,
                        country=country.lstrip(),
                    )
