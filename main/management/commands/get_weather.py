from django.core.management.base import BaseCommand
from main.management.weather_parser.parser_main import *


class Command(BaseCommand):
    help = 'Load weather from rp5.ru'

    def handle(self, *args, **kwargs):
        try:
            get_all_data()
        except Exception as e:
            self.stdout.write(f'Error is:\n{e}')
        else:
            self.stdout.write("Data was loaded")
