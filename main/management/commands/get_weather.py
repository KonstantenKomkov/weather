from django.core.management.base import BaseCommand
from main.management.weather_parser.main import *


class Command(BaseCommand):
    help = 'Load weather from rp5.ru'

    def handle(self, *args, **kwargs):
        get_all_data()
        self.stdout.write("Data was loaded")

        # create_csv_by_country('https://rp5.ru/Погода_в_России')