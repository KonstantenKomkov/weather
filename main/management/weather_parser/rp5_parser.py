from bs4 import BeautifulSoup
from collections import deque
from datetime import date
from random import randint, choice
from requests import Session, get
from requests.exceptions import HTTPError
from requests.models import Response
from time import sleep
from json import loads
from typing import Tuple

import main.management.weather_parser.rp5_ru_headers as rp5_ru_headers
import main.management.weather_parser.rp5_md_headers as rp5_md_headers
import main.management.weather_parser.yandex_headers as ya
from main.models import Country, WeatherStation, WeatherStationType
from weather.app_models import Yandex
from weather.settings import WEATHER_PARSER

browsers = ['Chrome', 'Firefox', 'Opera', 'Edge']


def get_start_date(s: str) -> date:
    """ Function get start date of observations for current weather station."""

    months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля',
              'августа', 'сентября', 'октября', 'ноября', 'декабря', ]
    if s.find(' номер метеостанции     , наблюдения с ') > -1:
        s = s.removeprefix(' номер метеостанции     , наблюдения с ')
    elif s.find(' аэропорт (ICAO)    , наблюдения с ') > -1:
        s = s.removeprefix(' аэропорт (ICAO)    , наблюдения с ')
    else:
        print(s)
        raise
    date_list: list = s.strip(' ').split(' ')
    year = int(date_list[2])
    month = months.index(date_list[1]) + 1
    day = int(date_list[0])
    return date(year, month, day)


def get_coordinates(a: str) -> tuple[float, float] | tuple[None, None]:
    """ Function find latitude and longitude in html string for weather station."""
    if isinstance(a, str):
        if a.find("show_map(") > -1 and a.find(");") > -1 and a.find(", ") > -1:
            temp = a[a.find("show_map(") + 9:a.find(");")].split(", ")
            return float(temp[0]), float(temp[1])
        return None, None
    else:
        raise (TypeError(f"must be str, not {type(a)}"))


def find_country_by_coordinates(yandex: Yandex, latitude, longitude) -> Country:
    """Function used yandex maps api and get country by coordinates."""

    data = {
        'login': yandex.login,
        'passwd': yandex.password,
    }

    # TODO: get session.headers or token and id from yandex
    response = Session().get(f'https://api-maps.yandex.ru/services/search//v2/?callback='
                             f'{yandex.id}&text={latitude}%2C{longitude}&format=json&rspn=0'
                             f'&lang=ru_RU&token={yandex.token}&type=geo&properties=addressdetails&'
                             f'geocoder_sco=latlong&origin=jsapi2Geocoder&apikey={yandex.api_key}',
                             data=data, headers=ya.header, )
    if response.text == '{"statusCode":401,"error":"Unauthorized","message":"Unauthorized"}':
        raise ValueError("Не удалось авторизоваться в API Yandex map - не можем получить название страны, установите "
                         "корректные значения для API Yandex map в config.ini, раздел yandex.")
    else:
        json_string = response.text.replace(f'/**/{yandex.id}(', '')
        json_string = json_string[:-2]
        data = loads(json_string)
        return Country(
            name=data["data"]["features"][len(data["data"]["features"]) - 1]["properties"]["GeocoderMetaData"]["Address\
            Details"]["Country"]["CountryName"])


def find_metar(soup) -> int:
    metar = -1
    founded_tags = soup.find_all("div", {"class": "archButton"})
    for tag in founded_tags:
        if tag.get('onclick').find('fFileMetarGet(') > -1:
            temp = tag.get('onclick')[tag.get('onclick').find('fFileMetarGet(') + 14:]
            temp = temp[:temp.find(')')]
            return int(temp.split(',')[1])
    return metar


def get_missing_ws_info(
        current_session: Session,
        station: WeatherStation,
        yandex: Yandex) -> Tuple[bool, WeatherStation | None]:
    """ Getting country, numbers weather station, start date of observations, from site rp5.ru."""

    try:
        response = current_session.get(station.rp5_link)
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        return True, None
    except Exception as err:
        print(f'Other error occurred: {err}')
        return True, None
    else:
        soup = BeautifulSoup(response.text, 'lxml')
        is_error = False
        if str(soup) == '<html><body><h1>Error 404. Page not found!</h1><br/></body></html>':
            is_error = True
        elif soup.find("img", src="/images/404.png") is not None:
            print('Find image with 404')
            is_error = True
        else:
            # Get station.number
            wmo_id = soup.find("input", id="wmo_id")
            cc_str = soup.find("input", id="cc_str")
            if wmo_id is not None:
                station.number = wmo_id.get('value')
                station.start_date = get_start_date(wmo_id.parent.text)
            elif cc_str is not None:
                station.number = cc_str.get('value')
                station.start_date = get_start_date(cc_str.parent.text)
            else:
                station.number = ''
                station.start_date = date(1, 1, 1)

            station.latitude, station.longitude = \
                get_coordinates(str(soup.find("div", class_="pointNaviCont noprint").find("a")))

            station.country = find_country_by_coordinates(yandex, station.latitude, station.longitude)
            station.metar = 0 if station.type.type == "" else find_metar(soup)
    return is_error, station


def get_text_with_link_on_weather_data_file(current_session: Session, number: str, start_date: date, last_date: date,
                                            url: str, data_type: WeatherStationType, metar: int | None) -> \
        tuple[Session, str | None]:
    """ Function create query for site rp5.ru with special params for
        getting JS text with link on csv.gz file and returns response of query.
        I use sessionw and headers because site return text - 'Error #FS000;'
        in otherwise.
    """
    phpsessid = get_phpsessid(current_session.cookies.items())
    # если сессия перестала быть актуальна

    try:
        if phpsessid is None:
            current_session.close()
            current_session = Session()
            current_session.get(url)
            phpsessid = get_phpsessid(current_session.cookies.items())

        if url == 'https://rp5.ru' and phpsessid is not None:
            current_session.headers = rp5_ru_headers.get_header(phpsessid, choice(browsers))
        elif url == 'https://rp5.md' and phpsessid is not None:
            current_session.headers = rp5_md_headers.get_header(phpsessid, 'Chrome')
        elif phpsessid is not None:
            current_session.headers = rp5_ru_headers.get_header(phpsessid, choice(browsers))
        else:
            print("Error: phpsessid is None!")
            return current_session, None

        response = None
        count = 5
        delay = WEATHER_PARSER['MAX_DELAY_BETWEEN_REQUESTS']
        while (response is None or response.text.find('http') == -1) and count > 0:
            if data_type.type == "метеостанция":
                response: Response = current_session.post(
                    f"{url}/responses/reFileSynop.php",
                    data={'wmo_id': number, 'a_date1': start_date.strftime('%d.%m.%Y'),
                          'a_date2': last_date.strftime('%d.%m.%Y'), 'f_ed3': 5, 'f_ed4': 5, 'f_ed5': 17, 'f_pe': 1,
                          'f_pe1': 2, 'lng_id': 2, })
            elif data_type.type == "METAR":
                response: Response = current_session.post(
                    f"{url}/responses/reFileMetar.php",
                    data={'metar': metar, 'a_date1': start_date.strftime('%d.%m.%Y'),
                          'a_date2': last_date.strftime('%d.%m.%Y'), 'f_ed3': 7, 'f_ed4': 7, 'f_ed5': 13, 'f_pe': 1,
                          'f_pe1': 2, 'lng_id': 2, })
            else:
                print(f"Error of data_type = {data_type.type}")
                return current_session, None
            count -= 1
            sleep(delay)
            delay += WEATHER_PARSER['MAX_DELAY_BETWEEN_REQUESTS']
        download_link: str | None = None
        if response is not None and response.text.find('http') > -1:
            download_link = get_link_archive_file(response.text)
        return current_session, download_link
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        return current_session, None
    except Exception as err:
        print(f'Other error occurred: {err}')
        return current_session, None


def get_link_archive_file(text: str) -> str | None:
    """ Function extract link on archive file with weather data from text."""

    link = None
    start_position: int = text.find('<a href=http')
    end_position: int = text.find('.csv.gz')
    if start_position > -1 and end_position > -1:
        link: str = text[start_position + 8:end_position + 7]
    else:
        print(f'Ссылка на скачивание архива не найдена! Text: "{text}"')
    return link


def get_pages_with_weather_at_place(pages: deque) -> tuple[list, list]:
    """Function find all pages with link at a place or find all places in country and links for it."""

    links, another = [], []

    while pages:
        response = get(pages.popleft())
        soup = BeautifulSoup(response.text, 'lxml')
        cells = soup.find_all(class_="countryMap-cell")

        for cell in cells:
            for a in cell.find_all('a'):
                if a.text == '>>>':
                    pages.append(f"https://rp5.ru{a['href']}")
                elif a['href'].find('/Погода_в_') > -1:
                    links.append(f'https://rp5.ru{a["href"]}')
                elif a['href'].find('Погода_в_') > -1:
                    links.append(f'https://rp5.ru/{a["href"]}')
                else:
                    another.append(a["href"])

        for page in pages:
            if page in links:
                links.remove(page)
    return links, another


def get_link_type(links: list, static_root: str, delimiter: str) -> list[list[str, str, int]]:
    """Function get links and types of weather stations by list of places links."""

    def get_place(url: str) -> str:
        """Function return name of place from url"""
        return url[url.find('Архив_погоды_в_') + 15:].replace("_", " ")

    def write_line(line: list) -> None:
        with open(f"{static_root}places.txt", "a+", encoding="utf-8") as file:
            file.write(f"{delimiter.join(map(str, line))}\n")

    result = list()
    current_session = Session()
    for i, link in enumerate(links):
        print(i)
        if i % WEATHER_PARSER['COUNT_REQUESTS_FOR_ONE_SESSION'] == 0:
            current_session = Session()
        response = current_session.get(link)
        soup = BeautifulSoup(response.text, 'lxml')
        nav_panel_list = soup.find_all(class_="pointNaviCont")
        for element in nav_panel_list:
            if element.find(class_="iconarchive") is not None:
                place = get_place(element.find("a")["href"])
                if [place, element.find("a")["href"], 0] not in result:
                    result.append([place, element.find("a")["href"], 0])
                    write_line([place, element.find("a")["href"], 0])
            elif element.find(class_="iconmetar") is not None:
                place = get_place(element.find("a")["href"])
                if [place, element.find("a")["href"], 1] not in result:
                    result.append([place, element.find("a")["href"], 1])
                    write_line([place, element.find("a")["href"], 1])
            elif element.find(class_="iconwug") is not None:
                place = get_place(element.find("a")["href"])
                if [place, element.find("a")["href"], 2] not in result:
                    result.append([place, element.find("a")["href"], 2])
                    write_line([place, element.find("a")["href"], 2])
        sleep(randint(WEATHER_PARSER['MIN_DELAY_BETWEEN_REQUESTS'], WEATHER_PARSER['MAX_DELAY_BETWEEN_REQUESTS']))
    return result


def get_phpsessid(items) -> str | None:
    phpsessid = None
    for x in items:
        if x[0] == 'PHPSESSID':
            phpsessid = x[1]
    return phpsessid
