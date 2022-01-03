from django.core.management.base import BaseCommand
from main.management.weather_parser.parser_main import *


class Command(BaseCommand):
    help = 'Load weather from rp5.ru'

    def handle(self, *args, **kwargs):
        # try:
        #     get_all_data()
        # except Exception as e:
        #     self.stdout.write(f'Error is:\n{e}')
        # else:
        #     self.stdout.write("Data was loaded")

        links_with_404 = get_all_data()
        self.stdout.write("Data was loaded.")
        self.stdout.write("Links which returned code 404:")
        if links_with_404:
            for station in links_with_404:
                self.stdout.write(station)

