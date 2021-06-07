from django.core.management.base import BaseCommand
from main.management.weather_parser.main import *


class Command(BaseCommand):
    help = 'Find sources weather from site rp5.ru. Total argument is start link for that country. ' \
           'Example for Russia link is https://rp5.ru/Погода_в_России.'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str, help=u'Link on country page')

    def handle(self, *args, **kwargs):
        url = kwargs['url']
        # Example: https://rp5.ru/Погода_в_России
        try:
            create_csv_by_country(url)
        except Exception as e:
            self.stdout.write(f'Error is:\n{e}')
        else:
            self.stdout.write("Sources was found")