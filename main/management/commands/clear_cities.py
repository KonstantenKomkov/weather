from django.core.management.base import BaseCommand
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
            _config = configparser.ConfigParser()
            _config.read("config.ini")
            delimiter = _config["csv"]["delimiter"]
            static_root: str = _config["path"]["static_root"]

            with open(f"{static_root}cities.txt", "r", encoding="utf-8") as file:
                lines: list[str] = file.readlines()
            for i, x in enumerate(lines):
                lines[i] = x.split(delimiter)[0:3]
                if lines[i][2] == '0':
                    lines[i][2] = '0\n'

            with open(f"{static_root}cities.txt", "w", encoding="utf-8") as file:
                for index, x in enumerate(lines):
                    file.write(delimiter.join(map(str, x)))
        except Exception as e:
            self.stdout.write(f'Error is:\n{e}')
        else:
            self.stdout.write("Cities was cleared to: place, link, type.")
