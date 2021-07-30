from django.core.management.base import BaseCommand
from main.management.weather_parser.main import *
import configparser


class Command(BaseCommand):
    help = 'Delete some data from text file:' \
           '- last date of loaded information or nothing;' \
           ' - id of weather station;' \
           ' - country;' \
           ' - city_id;' \
           ' - latitude;' \
           ' - longitude.'

    def handle(self, *args, **kwargs):
        try:
            config = configparser.ConfigParser()
            config.read("config.ini")
            DELIMITER = config["csv"]["delimiter"]
            STATIC_ROOT = config["path"]["static_root"]

            lines = []
            with open(f"{STATIC_ROOT}cities.txt", "r", encoding="utf-8") as file:
                lines = file.readlines()
            for i, line in enumerate(lines):
                lines[i] = line.split(DELIMITER)[0:3]
                if lines[i][2] == '0':
                    lines[i][2] = '0\n'

            with open(f"{STATIC_ROOT}cities.txt", "w", encoding="utf-8") as file:
                for index, line in enumerate(lines):
                    file.write(DELIMITER.join(map(str, line)))
        except Exception as e:
            self.stdout.write(f'Error is:\n{e}')
        else:
            self.stdout.write("Cities was cleared to: place, link, type.")