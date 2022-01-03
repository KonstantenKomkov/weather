from datetime import date, datetime, timedelta
from os import listdir, mkdir, path, remove

from requests import Session, Response
from random import randint
from time import sleep
import zlib
import configparser
from collections import deque
from psycopg2 import Error

from main.management.weather_parser.classes import WeatherStation
from main.management.weather_parser.db import db
import main.management.weather_parser.rp5_parser as rp5_parser
import main.management.weather_parser.processing as processing
import main.management.weather_parser.weather_csv as weather_csv
import main.management.weather_parser.queries as queries

config = configparser.ConfigParser()
config.read("config.ini")
DELIMITER = config["csv"]["delimiter"]
STATIC_ROOT = config["path"]["static_root"]
SAVE_IN_DB = False if config["db"]["database"] == '' else True
# Replace in config every time when you need update your sources
yandex = {
    "login": config["yandex"]["login"],
    "pass": config["yandex"]["pass"],
    "api_key": config["yandex"]["api_key"],
    "token": config["yandex"]["token"],
    "id": config["yandex"]["id"],
}

current_session: Session


def create_directory(ws: WeatherStation):
    try:
        mkdir(rf"{STATIC_ROOT}{ws.number}")
    except OSError as e:
        # 17 - FileExistsError, folder was created earlier.
        if e.errno != 17:
            raise
        pass


def get_weather_for_year(start_date: date, number: str, ws_id: int, url: str, data_type: int, metar: int):
    """ Function get archive file from site rp5.ru with weather data for one year
        and save it at directory."""

    global current_session, SAVE_IN_DB
    yesterday = datetime.now().date() - timedelta(days=1)
    if start_date < datetime.now().date():
        # Period must be year or less
        if datetime.now().date() > date(start_date.year, 12, 31):
            last_date: date = date(start_date.year, 12, 31)
        else:
            # minus one day because not all data for today will be load
            last_date: date = yesterday

        # Cookies might be empty, then get PHPSESSID
        if not current_session.cookies.items():
            current_session.get('https://rp5.ru/')

        answer = rp5_parser.get_text_with_link_on_weather_data_file(
            current_session, number, start_date, last_date, url, data_type, metar)
        count = 5
        while answer.text == "Error #FS000;" and count > 0:
            sleep(5)
            answer = rp5_parser.get_text_with_link_on_weather_data_file(
                current_session, number, start_date, last_date, url, data_type, metar)
            count -= 1
        else:
            if answer.text == "Error #FS000;":
                raise ValueError(f'Ссылка на скачивание архива не найдена! Text: {answer.text}')

        download_link = rp5_parser.get_link_archive_file(answer.text)

        with open(f'{STATIC_ROOT}{number}/{start_date.year}.csv', "wb") as file:
            response = current_session.get(download_link)
            while response.status_code != 200:
                response: Response = current_session.get(download_link)

            # unzip .gz archive
            decompress: bytes = zlib.decompress(response.content, wbits=zlib.MAX_WBITS | 16)
            csv_weather_data: str = decompress.decode('utf-8')

            if SAVE_IN_DB:
                if data_type == 0:
                    parsed_data: bytes = str.encode(processing.weather_stations_data_processing(
                        DELIMITER, csv_weather_data.splitlines(), ws_id))
                    file.write(parsed_data)
                elif data_type == 1:
                    parsed_data: bytes = str.encode(
                        processing.metar_data_processing(DELIMITER, csv_weather_data.splitlines(), ws_id))
                    file.write(parsed_data)
            else:
                file.write(str.encode(csv_weather_data))
        return True
    elif start_date == datetime.now().date():
        print('Data is actual.')
        return False
    else:
        raise ValueError(f"Query to future {start_date.strftime('%Y.%m.%d')}!")


def load_data_from_csv(folder: str, data_type: int):
    global STATIC_ROOT

    if path.isdir(f"{STATIC_ROOT}{folder}"):
        for weather_file in listdir(f"{STATIC_ROOT}{folder}"):
            if path.isfile(f"{STATIC_ROOT}{folder}\\{weather_file}") and weather_file[-4:] == '.csv':
                try:
                    if data_type == 0:
                        # TODO: Отказаться от использования pyDAL использовать встроенное в Django
                        db.executesql(queries.insert_csv_weather_station_data(
                            f"{STATIC_ROOT}{folder}\\{weather_file}",
                            DELIMITER))
                    elif data_type == 1:
                        # TODO: Отказаться от использования pyDAL использовать встроенное в Django
                        db.executesql(queries.insert_csv_metar_data(
                            f"{STATIC_ROOT}{folder}\\{weather_file}",
                            DELIMITER))
                    db.commit()
                except Error as e:
                    # UniqueViolation, was skipped because all directory will be check
                    if e.pgcode != '23505' and e.pgcode != '25P02':
                        # don't remove file for searching error
                        print(f"My error: {e.pgcode}. File in folder {folder}\\{weather_file}.")
                        raise
                    else:
                        remove(f"{STATIC_ROOT}{folder}\\{weather_file}")
                else:
                    remove(f"{STATIC_ROOT}{folder}\\{weather_file}")


def get_all_data() -> list[WeatherStation]:
    """ Function get all weather data for all weather stations from csv file
        from start date of observations to today or update data from date of last
        getting weather."""
    global current_session, yandex
    links_with_404: list[WeatherStation] = list()
    wanted_stations = weather_csv.read_csv_file(STATIC_ROOT, DELIMITER)

    indexes_of_duplicates = list()
    if wanted_stations:

        station: WeatherStation
        for index, station in enumerate(wanted_stations):

            current_session = Session()

            url = station.link[0:14]

            if station.start_date is None or station.number is None:
                status, station = rp5_parser.get_missing_ws_info(current_session, SAVE_IN_DB, station, yandex)
                print(f"Start getting data for {station.place} with "
                      f"start date of observations {station.start_date}...")

                # Link return code 404 - page not found
                if not status:
                    links_with_404.append(station)
                    continue
            else:
                print(f"Start getting data for {station.place} with last "
                      f"date of loading {(station.start_date - timedelta(days=1)).strftime('%Y.%m.%d')} ...")

            # На метеостанцию может быть несколько разных ссылок, поэтому надо проверять станции на уникальность по:
            # number, latitude, longitude
            unique = True
            if index != 0:
                for ws in wanted_stations[:index - 1]:
                    if station.number == ws.number and station.latitude == ws.latitude and \
                            station.longitude == ws.longitude:
                        indexes_of_duplicates.append(index)
                        unique = False
                        break
            if not unique:
                continue

            create_directory(station)
            start_year: int = station.start_date.year
            if SAVE_IN_DB:
                # Скользящая ошибка
                db.commit()
                count = 5
                while count > 0:
                    count -= 1
                    try:
                        x = queries.get_country_id(station.country)
                        # print(x)
                        temp = db.executesql(x)
                        # print(temp)
                        break
                    except Exception as e:
                        print(f'Error in country query: {e}')
                else:
                    print(f"Can't get country id from db after {count} attempts")
                    raise
                country_id = temp[0][0]
                # end of error
                place_id = db.executesql(queries.get_city_id(station.place, country_id))[0][0]
                station.ws_id = db.executesql(queries.get_ws_id(station, place_id, country_id))[0][0]
                db.commit()
            flag = False
            while start_year < datetime.now().year + 1:
                if start_year == station.start_date.year:
                    start_date: date = station.start_date
                else:
                    start_date: date = date(start_year, 1, 1)
                flag = get_weather_for_year(start_date, station.number, station.ws_id, url, station.data_type,
                                            station.metar)
                start_year += 1
            station.start_date = datetime.now().date() - timedelta(days=1)
            if flag:
                if SAVE_IN_DB:
                    load_data_from_csv(station.number, station.data_type)
                weather_csv.update_csv_file(STATIC_ROOT, DELIMITER, station, index)
                # Use timeout between sessions for concealment
                sleep(randint(3, 10))
                print("Data was loaded!")
            current_session.close()
    return links_with_404


def create_csv_by_country(url) -> None:
    """Function find all places, links and types (SYNOP, METAR, weather sensors) on site rp5.ru for country."""
    global STATIC_ROOT, DELIMITER

    pages = deque([url])
    # TODO: another variable isn't used. Она нужна чтобы посмотреть на ссылки, которые не были добавлены
    links, another = rp5_parser.get_pages_with_weather_at_place(pages)

    with open(f"{STATIC_ROOT}links.txt", "w", encoding="utf-8") as file:
        for link in links:
            file.write("%s\n" % link)

    links, lines = [], []
    with open(f"{STATIC_ROOT}links.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line in lines:
        links.append(line[:-1])

    # Получаем list[list[str - название места, str - url, int - тип]] ,
    # через каждые X ссылок начинаем новую сессию
    # TODO: вынести логику создания новой сессии в отдельную функцию
    rp5_parser.get_link_type(links, STATIC_ROOT, DELIMITER)

    # If you start find_sources command from the middle
    delete_not_unique_elements()


def delete_not_unique_elements() -> None:
    with open(f"{STATIC_ROOT}places.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()
        lines = list(set(lines))

    with open(f"{STATIC_ROOT}places.txt", "w", encoding="utf-8") as file:
        for line in lines:
            file.write(line)


def update_sources() -> None:
    with open(f"{STATIC_ROOT}places.txt", "r", encoding="utf-8") as file:
        sources: list = file.readlines()
    for i, source in enumerate(sources):
        sources[i] = source.split(DELIMITER)
        sources[i] = [sources[i][0], sources[i][1].replace('http', 'https'), sources[i][2]]

    with open(f"{STATIC_ROOT}cities.txt", "r", encoding="utf-8") as file:
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

    with open(f"{STATIC_ROOT}cities.txt", "a+", encoding="utf-8") as file:
        file.write('\n')
        for index, source in enumerate(sources):
            # Adding weather stations and metar
            if source[2] in ('0\n', '1\n', '0', '1'):
                if index == len(sources) - 1:
                    file.write(DELIMITER.join(map(str, source)))
                else:
                    file.write(DELIMITER.join(map(str, source)))
