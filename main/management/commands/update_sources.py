from django.core.management.base import BaseCommand
from main.management.weather_parser.parser_main import *


class Command(BaseCommand):
    help = 'Update sources weather from places.txt file to cities.csv.'

    def handle(self, *args, **kwargs):
        try:
            update_sources()
        except Exception as e:
            self.stdout.write(f'Error is:\n{e}')
        else:
            self.stdout.write("Sources was updated")