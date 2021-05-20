from datetime import date, datetime, timedelta
from os import listdir, mkdir, path, remove
from requests import Session
from random import randint
from time import sleep
import zlib
import configparser


import main.management.weather_parser.classes as classes
from main.management.weather_parser.db import db
import main.management.weather_parser.rp5_parser as rp5_parser
import main.management.weather_parser.processing as processing
import main.management.weather_parser.weather_csv as weather_csv
import main.management.weather_parser.queries as queries


config = configparser.ConfigParser()
config.read("config.ini")
DELIMITER = '#'
STATIC_ROOT = config["path"]["static_root"]
SAVE_IN_DB = False if config["db"]["database"] == '' else True


current_session: Session = None


def create_directory(ws: classes.WeatherStation):
    try:
        mkdir(rf"{STATIC_ROOT}{ws.number}")
    except OSError as e:
        # 17 - FileExistsError, folder was created earlier.
        if e.errno != 17:
            raise
        pass


def get_weather_for_year(start_date: date, number: int, ws_id: int, url: str):
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

        answer = rp5_parser.get_text_with_link_on_weather_data_file(current_session, number, start_date, last_date, url)
        count = 5
        while answer.text == "Error #FS000;" and count > 0:
            sleep(5)
            answer = rp5_parser.get_text_with_link_on_weather_data_file(
                current_session, number, start_date, last_date, url)
            count -= 1
        else:
            if answer.text == "Error #FS000;":
                raise ValueError(f'Ссылка на скачивание архива не найдена! Text: {answer.text}')

        download_link = rp5_parser.get_link_archive_file(answer.text)

        with open(f'{STATIC_ROOT}{number}/{start_date.year}.csv', "wb") as file:
            response = current_session.get(download_link)
            while response.status_code != 200:
                response = current_session.get(download_link)

            # unzip .gz archive
            decompress = zlib.decompress(response.content, wbits=zlib.MAX_WBITS | 16)
            csv_weather_data = decompress.decode('utf-8')

            if SAVE_IN_DB:
                file.write(processing.processing_data(DELIMITER, csv_weather_data.splitlines(), ws_id))
            else:
                file.write(csv_weather_data)
        return True
    elif start_date == datetime.now().date():
        print('Data is actual.')
        return False
    else:
        raise ValueError(f"Query to future {start_date.strftime('%Y.%m.%d')}!")


def load_data_from_csv(folder):
    global STATIC_ROOT

    if path.isdir(f"{STATIC_ROOT}{folder}"):
        for weather_file in listdir(f"{STATIC_ROOT}{folder}"):
            if path.isfile(f"{STATIC_ROOT}{folder}\\{weather_file}") and weather_file[-4:] == '.csv':
                try:
                    x = db.executesql(queries.insert_csv_weather_data(
                        f"{STATIC_ROOT}{folder}\\{weather_file}",
                        DELIMITER))
                    db.commit()
                except Exception as e:
                    # UniqueViolation, was skipped because all directory will be check
                    if e.pgcode != '23505':
                        # don't remove file for searching error
                        print(f"My error: {e.pgcode}")
                        raise
                    else:
                        remove(f"{STATIC_ROOT}{folder}\\{weather_file}")
                else:
                    remove(f"{STATIC_ROOT}{folder}\\{weather_file}")


def get_all_data():
    """ Function get all weather data for all weather stations from csv file
        from start date of observations to today or update data from date of last
        getting weather."""
    global current_session
    wanted_stations = weather_csv.read_csv_file(STATIC_ROOT, DELIMITER)

    if wanted_stations:

        station: classes.WeatherStation
        for index, station in enumerate(wanted_stations):

            current_session = Session()

            url = station.link[0:14]

            if station.start_date is None or station.number is None:
                rp5_parser.get_missing_ws_info(current_session, SAVE_IN_DB, station)
                print(f"Start getting data for {station.place} with "
                      f"start date of observations {station.start_date}...")
            else:
                print(f"Start getting data for {station.place} with last "
                      f"date of loading {(station.start_date-timedelta(days=1)).strftime('%Y.%m.%d')} ...")

            create_directory(station)
            start_year: int = station.start_date.year
            if SAVE_IN_DB:
                country_id = db.executesql(queries.get_country_id(station.country))[0][0]
                city_id = db.executesql(queries.get_city_id(station.place, country_id))[0][0]
                station.ws_id = db.executesql(queries.get_ws_id(station, city_id, country_id))[0][0]
                db.commit()
            flag = False
            while start_year < datetime.now().year + 1:
                if start_year == station.start_date.year:
                    start_date: date = station.start_date
                else:
                    start_date: date = date(start_year, 1, 1)
                flag = get_weather_for_year(start_date, station.number, station.ws_id, url)
                start_year += 1
            station.start_date = datetime.now().date() - timedelta(days=1)
            if flag:
                if SAVE_IN_DB:
                    load_data_from_csv(station.number)
                weather_csv.update_csv_file(STATIC_ROOT, DELIMITER, station, index)
                # Use timeout between sessions for concealment
                sleep(randint(3, 10))
                print("Data was loaded!")
            current_session.close()
    return


def create_csv_by_country(url):
    """Function find all placec, links and types (SYNOP, METAR, weather sensors) on site rp5.ru for country."""
    global STATIC_ROOT, DELIMITER

    pages = deque([url])
    links, another = rp5_parser.get_pages_with_weather_at_place(STATIC_ROOT, pages)

    with open(f"{STATIC_ROOT}links.txt", "w", encoding="utf-8") as file:
        for link in links:
            file.write("%s\n" % link)

    links, lines = [], []
    with open(f"{STATIC_ROOT}links.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line in lines:
        links.append(line[:-1])

    temp = links[6655:]

    links_and_types = rp5_parser.get_link_type(temp, STATIC_ROOT, DELIMITER)
