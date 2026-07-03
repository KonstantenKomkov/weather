from datetime import datetime

from main.models import Cloudiness

# data from table 'wind_directions'
wind_direction = ['ветер, дующий с юга', 'ветер, дующий с юго-востока', 'ветер, дующий с востока',
                  'штиль, безветрие', 'ветер, дующий с юго-юго-востока', 'ветер, дующий с северо-востока',
                  'ветер, дующий с северо-северо-востока', 'ветер, дующий с западо-северо-запада',
                  'ветер, дующий с северо-северо-запада', 'ветер, дующий с востоко-северо-востока',
                  'ветер, дующий с юго-запада', 'ветер, дующий с юго-юго-запада',
                  'ветер, дующий с западо-юго-запада', 'ветер, дующий с запада',
                  'ветер, дующий с северо-запада', 'ветер, дующий с севера',
                  'ветер, дующий с востоко-юго-востока', 'переменное направление', ]
# data from table 'cloudiness'
cloud_cover = ['Облаков нет.', '10%  или менее, но не 0', '20–30', '40', '50', '60',
               '70 – 80', '90  или более, но не 100%', '100',
               'Небо не видно из-за тумана и/или других метеорологических явлений.', ]
# data from table 'cloudiness_cl'
count_cloud_cover_nh = ['Облаков нет.', '10%  или менее, но не 0', '20–30', '40', '50', '60',
                        '70 – 80', '90  или более, но не 100%', '100', 'null',
                        'Небо не видно из-за тумана и/или других метеорологических явлений.', ]

_cloudiness_by_description: dict[str, int] | None = None


def _get_cloudiness_cache() -> dict[str, int]:
    global _cloudiness_by_description
    if _cloudiness_by_description is None:
        _cloudiness_by_description = {
            row.description: row.pk for row in Cloudiness.objects.all()
        }
    return _cloudiness_by_description


def get_cloudiness_id(value: str) -> int:
    cache = _get_cloudiness_cache()
    if value in cache:
        return cache[value]
    cloudiness, _created = Cloudiness.objects.get_or_create(description=value)
    cache[value] = cloudiness.pk
    return cloudiness.pk


def weather_stations_data_processing(delimiter: str, csv_weather_data: list, ws_id: int) -> str:
    """ Processing data for database. Check models.py for see database structure."""
    global wind_direction, cloud_cover, count_cloud_cover_nh
    weathers_header = \
        f'weather_station_id{delimiter} "date"{delimiter} temperature{delimiter} pressure{delimiter} ' \
        f'pressure_converted{delimiter} baric_trend{delimiter} humidity{delimiter} wind_direction_id{delimiter} ' \
        f'wind_speed{delimiter} max_wind_speed{delimiter} max_wind_speed_between{delimiter} ' \
        f'cloud_cover_id{delimiter} current_weather{delimiter} past_weather{delimiter} past_weather_two{delimiter} ' \
        f'min_temperature{delimiter} max_temperature{delimiter} cloud_one{delimiter} cloud_count_id{delimiter} ' \
        f'cloud_hight{delimiter} cloud_two{delimiter} cloud_three{delimiter} visibility{delimiter} ' \
        f'dew_point{delimiter} rainfall{delimiter} rainfall_time{delimiter} soil_condition{delimiter} ' \
        f'soil_temperature{delimiter} soil_with_snow{delimiter} snow_hight\n'

    del csv_weather_data[:7]
    for x in csv_weather_data:
        line_list = x.split('";"')
        line_list[0] = line_list[0][1:-1]
        line_list[-1] = line_list[-1].replace('";', '')

        for i, row in enumerate(line_list):
            if row == '' or row == ' ':
                line_list[i] = 'null'

        line_list[0] = datetime.strptime(line_list[0], '%d.%m.%Y %H:%M')

        # temperature
        if line_list[1] != 'null':
            if float(line_list[1]) < -100 or float(line_list[1]) > 100:
                line_list[1] = 'null'

        # min_temperature
        if line_list[14] != 'null':
            if float(line_list[14]) < -100 or float(line_list[14]) > 100:
                line_list[14] = 'null'

        # max_temperature
        if line_list[15] != 'null':
            if float(line_list[15]) < -100 or float(line_list[15]) > 100:
                line_list[15] = 'null'

        if line_list[10] == 'null':
            line_list[10] = 10
        else:
            line_list[10] = cloud_cover.index(line_list[10].replace('%.', '')) + 1
        line_list[17] = count_cloud_cover_nh.index(line_list[17].replace('%.', '')) + 1

        if line_list[6].lower() in wind_direction:
            try:
                line_list[6] = wind_direction.index(line_list[6].lower()) + 1
            except Exception as e:
                print(line_list[6].lower())
                print(e)
        else:
            line_list[6] = 'null'

        if line_list[21].find('менее ') > -1:
            line_list[21] = line_list[21].replace('менее ', '')

        # incorrect value for pressure
        if line_list[2] != 'null':
            if float(line_list[2]) < 500 or float(line_list[2]) > 900:
                line_list[2] = 'null'

        temp = f'{delimiter}'.join(map(str, line_list))
        weathers_header = f"{weathers_header}{ws_id}{delimiter}{temp}\n"

    if weathers_header[-2:-1] == '\n':
        weathers_header = weathers_header[:-2]
    return weathers_header.encode('utf-8')


def metar_data_processing(delimiter: str, csv_weather_data: list, ws_id: int) -> str:
    """ Processing data for database. Check models.py for see database structure."""
    global wind_direction

    metars_header = \
        f'weather_station_id{delimiter} "date"{delimiter} temperature{delimiter} pressure{delimiter} ' \
        f'pressure_converted{delimiter} humidity{delimiter} wind_direction_id{delimiter} wind_speed{delimiter} ' \
        f'max_wind_speed{delimiter} current_weather{delimiter} past_weather{delimiter} cloud_cover_id{delimiter} ' \
        f'visibility{delimiter} dew_point\n'

    del csv_weather_data[:7]
    for x in csv_weather_data:
        line_list = x.split('";"')
        line_list[0] = line_list[0][1:-1]
        line_list[-1] = line_list[-1].replace('";', '')

        for i, row in enumerate(line_list):
            if row == '' or row == ' ':
                line_list[i] = 'null'

        line_list[0] = datetime.strptime(line_list[0], '%d.%m.%Y %H:%M')

        # temperature
        if line_list[1] != 'null':
            if float(line_list[1]) < -100 or float(line_list[1]) > 100:
                line_list[1] = 'null'

        if line_list[10] == 'null':
            line_list[10] = 10
        else:
            line_list[10] = get_cloudiness_id(line_list[10])

        if line_list[5].lower() in wind_direction:
            line_list[5] = wind_direction.index(line_list[5].lower()) + 1
        else:
            line_list[5] = 'null'

        # incorrect value for pressure
        if line_list[2] != 'null':
            if float(line_list[2]) < 500 or float(line_list[2]) > 900:
                line_list[2] = 'null'

        if line_list[11].find(' и более') > -1:
            line_list[11] = line_list[11][:line_list[11].find(' и более')]
        temp = f'{delimiter}'.join(map(str, line_list))
        metars_header = f"{metars_header}{ws_id}{delimiter}{temp}\n"

    if metars_header[-2:-1] == '\n':
        metars_header = metars_header[:-2]
    return metars_header.encode('utf-8')
