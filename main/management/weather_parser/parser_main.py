from datetime import date, datetime, timedelta
from os import listdir, mkdir, path, remove
from typing import AnyStr
from requests import Session, Response
from random import randint
from time import sleep
import zlib
from collections import deque
from psycopg2 import Error
from main.management.weather_parser.db import db
import main.management.weather_parser.rp5_parser as rp5_parser
import main.management.weather_parser.processing as processing
import main.management.weather_parser.weather_csv as weather_csv
import main.management.weather_parser.queries as queries
from weather.settings import app, WEATHER_PARSER, STATIC_ROOT
from main.models import Country, Place, WeatherStation

SAVE_IN_DB: bool = False if app.database.name == '' else True
DELIMITER: str = WEATHER_PARSER['CSV_DELIMITER']
_STATIC_ROOT = f"{STATIC_ROOT}\\csv_data\\"
current_session = Session()
now: datetime = datetime.now()
yesterday: date = now.date() - timedelta(days=1)


def get_all_data() -> None:
    """ Function get all weather data for all weather stations from csv file
        from start date of observations to today or update data from date of last
        getting weather."""
    global current_session, now, yesterday

    links_with_error: list[WeatherStation] = list()
    wanted_stations = weather_csv.read_csv_file(_STATIC_ROOT, DELIMITER)
    countries: list[Country] = []
    places: list[Place] = []
    weather_stations: list[WeatherStation] = []

    indexes_of_duplicates = list()
    if wanted_stations:
        if SAVE_IN_DB:
            countries = list(Country.objects.all())
            places = list(Place.objects.all())
            weather_stations = list(WeatherStation.objects.all())

        station: WeatherStation
        for index, station in enumerate(wanted_stations):
            if index > 0:
                current_session = recreate_session(current_session)

            if station.start_date is None or station.number is None:
                is_error, station = rp5_parser.get_missing_ws_info(current_session, station, app.yandex)
                print(f"Start getting data for {station.place} with "
                      f"start date of observations {station.start_date}...")

                # Link return code 404 or another error
                if is_error:
                    links_with_error.append(station)
                    print("Error link - data not loaded")
                    continue
                else:
                    # На метеостанцию может быть несколько разных ссылок, поэтому надо проверять станции на
                    # уникальность по: number, latitude, longitude
                    unique = True

                    if index != 0:
                        for ws in wanted_stations[:index - 1]:
                            if station.number == ws.number and station.latitude == ws.latitude and \
                                    station.longitude == ws.longitude:
                                indexes_of_duplicates.append(index)
                                unique = False
                                break
                    if not unique:
                        print("Not unique link - data not loaded")
                        continue
                    if station.start_date == now.date():
                        print("Start date of observations for that station is today, we should get all weather date "
                              "tomorrow")
                        continue
            elif station.start_date - timedelta(days=1) == yesterday:
                print("Data is actual")
                continue
            else:
                print(f"Start getting data for {station.place} with last "
                      f"date of loading {(station.start_date - timedelta(days=1)).strftime('%Y.%m.%d')} ...")

            create_directory(station)
            start_year: int = station.start_date.year
            if SAVE_IN_DB:
                country_id: int | None = None
                place_id: int | None = None

                if countries:
                    for country in countries:
                        if country.name == station.country:
                            country_id = country.pk
                            break
                if country_id is None:
                    new_country: Country = Country(name=station.country.name)
                    new_country.save()
                    countries.append(new_country)
                    country_id = new_country.pk

                if places:
                    for place in places:
                        if place.name == station.place and place.country == country_id:
                            place_id = place.pk
                            break

                if place_id is None:
                    new_place: Place = Place(name=station.place.name, country=country_id)
                    new_place.save()
                    places.append(new_place)
                    place_id = new_place.pk

                if weather_stations:
                    for weather_station in weather_stations:
                        if weather_station.country == country_id and \
                                weather_station.place == place_id and \
                                weather_station.number == station.number and \
                                weather_station.rp5_link == station.rp5_link and \
                                weather_station.data_type == station.data_type:
                            station = weather_station
                            break
                if station.pk is None:
                    # TODO: писать сразу station to db?
                    new_weather_station: WeatherStation = WeatherStation(
                        number=station.number,
                        latitude=station.latitude,
                        longitude=station.longitude,
                        rp5_link=station.rp5_link,
                        last_date=station.last_date,
                        data_type=station.data_type,
                        place=place_id,
                        country=country_id,
                        metar=station.metar
                    )
                    new_weather_station.save()
                    wanted_stations.append(new_weather_station)
                    station = new_weather_station

                # # Скользящая ошибка
                # count = 5
                # while count > 0:
                #     count -= 1
                #     try:
                #         x = queries.get_country_id(station.country)
                #         print(x)
                #         temp = db.executesql(x)
                #         db.commit()
                #         break
                #     except Exception as e:
                #         print('Ошибка:\n', traceback.format_exc())
                #         print(f'Error in country query: {e}')
                # else:
                #     print(f"Can't get country id from db after {count} attempts")
                #     raise
                # country_id = temp[0][0]
                # # end of error

                # place_id = db.executesql(queries.get_city_id(station.place, country_id))[0][0]
                # db.commit()
                # station.ws_id = db.executesql(queries.get_ws_id(station, place_id, country_id))[0][0]
                # db.commit()
            flag = False
            while start_year < now.year + 1:
                if start_year == station.start_date.year:
                    start_date: date = station.start_date
                else:
                    start_date: date = date(start_year, 1, 1)
                flag = get_weather_for_year(start_date, station.number, station.pk, station.rp5_link[0:14],
                                            station.data_type,
                                            station.metar)
                start_year += 1
            station.start_date = yesterday
            if flag:
                if SAVE_IN_DB:
                    load_data_from_csv(station.number, station.data_type)
                weather_csv.update_csv_file(_STATIC_ROOT, DELIMITER, station, index)
                # Use timeout between sessions for concealment
                sleep(randint(WEATHER_PARSER['MIN_DELAY_BETWEEN_REQUESTS'],
                              WEATHER_PARSER['MAX_DELAY_BETWEEN_REQUESTS']))
                print("Data was loaded!")
    weather_csv.delete_duplicates_weather_stations(indexes_of_duplicates, len(wanted_stations), _STATIC_ROOT)
    print("All data was loaded.")

    if links_with_error:
        print("Links which returned code 404 or another errors:")
        for station in links_with_error:
            print(station)


def get_weather_for_year(start_date: date, number: str, ws_id: int, url: str, data_type: int, metar: int) -> bool:
    """ Function get archive file from site rp5.ru with weather data for one year
        and save it at directory."""

    global current_session, SAVE_IN_DB, now, yesterday
    if start_date < now.date():
        # Period must be year or less
        if now.date() > date(start_date.year, 12, 31):
            last_date: date = date(start_date.year, 12, 31)
        else:
            # minus one day because not all data for today will be load
            last_date: date = yesterday

        # Cookies might be empty, then get PHPSESSID
        if not current_session.cookies.items():
            current_session.get(url)

        answer: Response = rp5_parser.get_text_with_link_on_weather_data_file(
            current_session, number, start_date, last_date, url, data_type, metar)
        count = 5
        # while (answer.text == "Error #FS000;" or answer.text == "Error #FM004;" or answer.text == "") and count > 0:
        while answer.text.find('http') == -1 and count > 0:
            sleep(WEATHER_PARSER['MAX_DELAY_BETWEEN_REQUESTS'])
            answer = rp5_parser.get_text_with_link_on_weather_data_file(
                current_session, number, start_date, last_date, url, data_type, metar)
            count -= 1
        else:
            print(f"{count=}")
            if answer.text == "Error #FS000;" or answer.text == "Error #FM004;" or answer.text == "":
                print(f'Ссылка на скачивание архива не найдена! Text: {answer.text}')
                return False
            # if answer.text == "Error #FS000;":
            #     raise ValueError(f'Ссылка на скачивание архива не найдена! Text: {answer.text}')
            # raise ValueError(f'Ссылка на скачивание архива не найдена! Text: {answer.text}')

        download_link: str = rp5_parser.get_link_archive_file(answer.text)

        with open(f'{_STATIC_ROOT}{number}/{start_date.year}.csv', "wb") as file:
            response: Response = current_session.get(download_link)
            while response.status_code != 200:
                response = current_session.get(download_link)

            # unzip .gz archive
            decompress: bytes = zlib.decompress(response.content, wbits=zlib.MAX_WBITS | 16)
            csv_weather_data: str = decompress.decode('utf-8')

            if SAVE_IN_DB:
                if data_type == 0:
                    parsed_data: AnyStr = processing.weather_stations_data_processing(
                        DELIMITER, csv_weather_data.splitlines(), ws_id)
                    file.write(parsed_data)
                elif data_type == 1:
                    parsed_data: AnyStr = \
                        processing.metar_data_processing(DELIMITER, csv_weather_data.splitlines(), ws_id)
                    file.write(parsed_data)
            else:
                file.write(str.encode(csv_weather_data))
        return True
    else:
        raise ValueError(f"Query to future {start_date.strftime('%Y.%m.%d')}!")


def load_data_from_csv(folder: str, data_type: int) -> None:
    global _STATIC_ROOT

    if path.isdir(f"{_STATIC_ROOT}{folder}"):
        for weather_file in listdir(f"{_STATIC_ROOT}{folder}"):
            if path.isfile(f"{_STATIC_ROOT}{folder}\\{weather_file}") and weather_file[-4:] == '.csv':
                try:
                    if data_type == 0:
                        # TODO: Отказаться от использования pyDAL использовать встроенное в Django
                        db.executesql(queries.insert_csv_weather_station_data(
                            f"{_STATIC_ROOT}{folder}\\{weather_file}",
                            DELIMITER))
                    elif data_type == 1:
                        # TODO: Отказаться от использования pyDAL использовать встроенное в Django
                        db.executesql(queries.insert_csv_metar_data(
                            f"{_STATIC_ROOT}{folder}\\{weather_file}",
                            DELIMITER))
                    db.commit()
                except Error as e:
                    # UniqueViolation, was skipped because all directory will be check
                    if e.pgcode != '23505' and e.pgcode != '25P02':
                        # don't remove file for searching error
                        print(f"My error: {e.pgcode}. File in folder {folder}\\{weather_file}.")
                        raise
                    else:
                        if not WEATHER_PARSER['DELETE_CSV_FILES']:
                            remove(f"{_STATIC_ROOT}{folder}\\{weather_file}")
                else:
                    if not WEATHER_PARSER['DELETE_CSV_FILES']:
                        remove(f"{_STATIC_ROOT}{folder}\\{weather_file}")


def create_csv_by_country(url) -> None:
    """Function find all places, links and types (SYNOP, METAR, weather sensors) on site rp5.ru for country."""
    global _STATIC_ROOT, DELIMITER

    pages = deque([url])
    links, another = rp5_parser.get_pages_with_weather_at_place(pages)

    if len(another) > 0:
        print(f"Another links which was not included in links array\n {another}")

    with open(f"{_STATIC_ROOT}links.txt", "w", encoding="utf-8") as file:
        for link in links:
            file.write("%s\n" % link)

    links, lines = [], []
    with open(f"{_STATIC_ROOT}links.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line in lines:
        links.append(line[:-1])

    # Получаем list[list[str - название места, str - url, int - тип]] ,
    # через каждые X ссылок начинаем новую сессию
    rp5_parser.get_link_type(links, _STATIC_ROOT, DELIMITER)

    # If you start find_sources command from the middle
    delete_not_unique_elements()


def delete_not_unique_elements() -> None:
    with open(f"{_STATIC_ROOT}places.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()
        lines = list(set(lines))

    with open(f"{_STATIC_ROOT}places.txt", "w", encoding="utf-8") as file:
        for line in lines:
            file.write(line)


def update_sources() -> None:
    with open(f"{_STATIC_ROOT}places.txt", "r", encoding="utf-8") as file:
        sources: list = file.readlines()
    for i, source in enumerate(sources):
        sources[i] = source.split(DELIMITER)
        sources[i] = [sources[i][0], sources[i][1].replace('http', 'https'), sources[i][2]]

    with open(f"{_STATIC_ROOT}cities.txt", "r", encoding="utf-8") as file:
        lines: list = file.readlines()
    for i, line in enumerate(lines):
        lines[i] = line.split(DELIMITER)

    # Deleting all that in cities.csv already
    new_line_list = list()
    count = 0
    for line in lines:
        for source in sources.copy():
            if source[1] == line[1]:
                new_line_list.append(line)
                sources.remove(source)
                count += 1

    # print(len(sources))
    # print(f"{count=}")

    with open(f"{_STATIC_ROOT}cities.txt", "a+", encoding="utf-8") as file:
        file.write('\n')
        for index, source in enumerate(sources):
            # Adding weather stations and metar
            if source[2] in ('0\n', '1\n', '0', '1'):
                if index == len(sources) - 1:
                    file.write(DELIMITER.join(map(str, source)))
                else:
                    file.write(DELIMITER.join(map(str, source)))


def create_directory(ws: WeatherStation) -> None:
    try:
        mkdir(rf"{_STATIC_ROOT}{ws.number}")
    except OSError as e:
        # 17 - FileExistsError, folder was created earlier.
        if e.errno != 17:
            raise
        pass


def recreate_session(session: Session) -> Session:
    session.close()
    session = Session()
    return session
