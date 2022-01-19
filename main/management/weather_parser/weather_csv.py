from datetime import datetime, timedelta
from main.models import Country, Place, WeatherStation


def read_csv_file(static_root: str, delimiter: str) -> [WeatherStation]:
    """ Get data about new weather stations from csv file for site rp5.ru.
        Csv file structure:
        - place;
        - link on weathers archive page for place in site rp5.ru;
        - data type (0 - weather station, 1 - metar, 2 - weather sensor);
        - last date of loaded information or nothing;
        - id of weather station or nothing;
        - country or nothing;
        - city_id or nothing;
        - latitude or nothing;
        - longitude or nothing.
    """

    stations: list[WeatherStation] = list()
    with open(f"{static_root}cities.txt", 'r', encoding="utf-8") as f:
        for line in f:
            temp = line.strip('\n').split(delimiter)
            if len(temp) > 3:
                stations.append(WeatherStation(
                    place=Place(name=temp[0], country=Country(name=temp[5] if temp[5] != 'None' else None),),
                    rp5_link=temp[1],
                    data_type=int(temp[2]),
                    last_date=datetime.strptime(temp[3], '%Y-%m-%d').date() + timedelta(days=1)
                    if temp[3] != 'None' else None,
                    number=temp[4] if temp[4] != 'None' else None,
                    country=Country(name=temp[5] if temp[5] != 'None' else None),
                    pk=int(temp[6]) if temp[6] != 'None' else None,
                    latitude=float(temp[7]) if temp[7] != 'None' else None,
                    longitude=float(temp[8]) if temp[8] != 'None' else None,
                    metar=int(temp[9]),))
            else:
                stations.append(WeatherStation(
                    place=Place(name=temp[0], country=Country()),
                    rp5_link=temp[1],
                    data_type=int(temp[2]),
                    country=Country(),
                ))
    return stations


def update_csv_file(static_root: str, delimiter: str, station: WeatherStation, index: int):
    """ Function update file with our wanted weather stations.
        It write current date and id of weather station."""

    with open(f"{static_root}cities.txt", "r+", encoding="utf-8") as csv_file:
        lines_list = csv_file.readlines()
        line_list = lines_list[index].split(delimiter)
        if line_list[1] == station.rp5_link:
            if len(line_list) == 3:
                lines_list[index] = f"{station.to_csv(delimiter)}\n"
                csv_file.seek(0)
                csv_file.write("".join(lines_list))
            else:
                line_list[3] = station.start_date.strftime("%Y-%m-%d")
                updated_line = delimiter.join(line_list)
                lines_list[index] = f"{updated_line}"
                csv_file.seek(0)
                csv_file.write("".join(lines_list))


def delete_duplicates_weather_stations(indexes_of_duplicates: list, len_ws_list: int, static_root):

    with open(f"{static_root}cities.txt", "r", encoding="utf-8") as csv_file:
        lines_list = csv_file.readlines()

    if len(lines_list) == len_ws_list:
        with open(f"{static_root}cities.txt", "w", encoding="utf-8") as csv_file:
            for i, line in enumerate(lines_list):
                if i not in indexes_of_duplicates:
                    csv_file.write(line)
    else:
        print("Duplicates can't be delited, because length of wanted_stations and count of lines are not equal")
