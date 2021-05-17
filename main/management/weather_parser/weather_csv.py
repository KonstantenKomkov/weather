import main.management.weather_parser.classes as classes
from datetime import datetime, timedelta


def read_new_cities(static_root: str, delimiter: str) -> [classes.WeatherStation]:
    """ Get data about new weather stations from csv file for site rp5.ru.
        Csv file structure:
        - city;
        - link on weathers archive page for city in site rp5.ru;
        - data type (0 - weather station, 1 - metar, 2 - weather sensor);
        - last date of loaded information or nothing;
        - id of weather station or nothing;
        - country or nothing;
        - city_id or nothing;
        - latitude or nothing;
        - longitude or nothing.
    """

    stations: list[classes.WeatherStation] = list()
    with open(f"{static_root}cities.txt", 'r', encoding="utf-8") as f:
        for line in f:
            temp = line.strip('\n').split(delimiter)
            if len(temp) > 3:
                stations.append(classes.WeatherStation(
                    city=temp[0],
                    link=temp[1],
                    data_type=int(temp[2]),
                    start_date=datetime.strptime(temp[3], '%Y-%m-%d').date() + timedelta(days=1)
                    if temp[3] != 'None' else None,
                    number=int(temp[4]) if temp[4] != 'None' else None,
                    country=temp[5] if temp[5] != 'None' else None,
                    ws_id=int(temp[6]) if temp[6] != 'None' else None,
                    latitude=temp[7] if temp[7] != 'None' else None,
                    longitude=temp[8] if temp[8] != 'None' else None,))
            else:
                stations.append(classes.WeatherStation(
                    city=temp[0],
                    link=temp[1],
                    data_type=int(temp[2])))
    return stations


def update_csv_file(static_root: str, delimiter, station: classes.WeatherStation, index: int):
    """ Function update file with our wanted weather stations.
        It write current date and id of weather station."""

    with open(f"{static_root}cities.txt", "r+", encoding="utf-8") as csv_file:
        lines_list = csv_file.readlines()
        line_list = lines_list[index].split("#")
        if line_list[1] == station.link:
            line_list[3] = station.start_date.strftime("%Y-%m-%d")
            updated_line = "#".join(line_list)
            lines_list[index] = updated_line
            csv_file.seek(0)
            csv_file.write("".join(lines_list))
