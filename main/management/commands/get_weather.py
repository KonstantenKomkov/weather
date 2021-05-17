from django.core.management.base import BaseCommand
from main.management.weather_parser.main import *


class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):
        get_all_data()

        # Should be call once before insert data to database
        # db.executesql(queries.insert_wind_data)
        # db.executesql(queries.insert_cloudiness_data)
        # db.executesql(queries.insert_cloudiness_cl_data())
        # db.commit()

        # if SAVE_IN_DB:
        #     load_data_to_database()
        # self.stdout.write("Data was loaded")
