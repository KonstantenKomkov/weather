from bs4 import BeautifulSoup
from collections import deque
from datetime import date
from random import randint, choice
from requests import Session, get
from requests.exceptions import HTTPError
from requests.models import Response
from time import sleep


import main.management.weather_parser.rp5_ru_headers as rp5_ru_headers
import main.management.weather_parser.rp5_md_headers as rp5_md_headers
import main.management.weather_parser.classes as classes


browsers = ['Chrome', 'Firefox', 'Yandex']


def get_start_date(s: str) -> date:
    """ Function get start date of observations for current weather station."""

    months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля',
              'августа', 'сентября', 'октября', 'ноября', 'декабря', ]
    s = s.removeprefix(' номер метеостанции     , наблюдения с ')
    date_list: list = s.strip(' ').split(' ')
    year = int(date_list[2])
    month = months.index(date_list[1]) + 1
    day = int(date_list[0])
    return date(year, month, day)


def get_coordinates(a: str) -> tuple[float, float]:
    """ Function find latitude and longitude in html string for weather station."""
    if isinstance(a, str):
        if a.find("show_map(") > -1 and a.find(");") > -1 and a.find(", ") > -1:
            temp = a[a.find("show_map(") + 9:a.find(");")].split(", ")
            return float(temp[0]), float(temp[1])
        return None, None
    else:
        raise (TypeError(f"must be str, not {type(a)}"))


def get_missing_ws_info(current_session: Session, save_in_db: bool, station: classes.WeatherStation) -> \
        classes.WeatherStation:
    """ Getting country, numbers weather station, start date of observations, from site rp5.ru."""

    try:
        response = current_session.get(station.link)
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        soup = BeautifulSoup(response.text, 'lxml')
        station.number = soup.find("input", id="wmo_id").get('value')
        station.start_date = get_start_date(soup.find("input", id="wmo_id").parent.text)
        country_span = soup.find("div", class_="intoLeftNavi").find("span", class_="verticalBottom")
        for index, child in enumerate(country_span):
            if index == 5:
                station.country = child.find("nobr").text
                break
        station.latitude, station.longitude = \
            get_coordinates(str(soup.find("div", class_="pointNaviCont noprint").find("a")))
        # if save_in_db:
        #     if station.city_id is None:
        #         station.city_id = queries.get_id_from_db()
    return station


def get_text_with_link_on_weather_data_file(current_session: Session, ws_id: int, start_date: date, last_date: date,
                                            url: str):
    """ Function create query for site rp5.ru with special params for
        getting JS text with link on csv.gz file and returns response of query.
        I use sessionw and headers because site return text - 'Error #FS000;'
        in otherwise.
    """
    phpsessid = None
    for x in current_session.cookies.items():
        if x[0] == 'PHPSESSID':
            phpsessid = x[1]
    if url == 'https://rp5.ru':
        current_session.headers = rp5_ru_headers.get_header(current_session.cookies.items()[0][1], choice(browsers))
    elif url == 'https://rp5.md':
        current_session.headers = rp5_md_headers.get_header(phpsessid, 'Chrome')
    else:
        current_session.headers = rp5_ru_headers.get_header(current_session.cookies.items()[0][1], choice(browsers))
    try:
        result: Response = current_session.post(
            f"{url}/responses/reFileSynop.php",
            data={'wmo_id': ws_id, 'a_date1': start_date.strftime('%d.%m.%Y'),
                  'a_date2': last_date.strftime('%d.%m.%Y'), 'f_ed3': 5, 'f_ed4': 5, 'f_ed5': 17, 'f_pe': 1,
                  'f_pe1': 2, 'lng_id': 2, })
        return result
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')


def get_link_archive_file(text: str) -> str:
    """ Function extract link on archive file with weather data from text."""

    start_position: int = text.find('<a href=http')
    end_position: int = text.find('.csv.gz')
    if start_position > -1 and end_position > -1:
        link: str = text[start_position + 8:end_position + 7]
    else:
        raise ValueError(f'Ссылка на скачивание архива не найдена! Text: "{text}"')
    return link


def get_pages_with_weather_at_place(static_root: str, pages: deque) -> deque:
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


def get_link_type(links: list, static_root, delimiter) -> list:
    """Function get links and types of weather stations by list of places links."""

    def get_place(url: str) -> str:
        place = url[url.find('Архив_погоды_в_')+15:].replace("_", " ")
        return place


    def write_line(static_root: str, line: list, delimiter: str):
        with open(f"{static_root}places.txt", "a+", encoding="utf-8") as file:
            file.write(f"{delimiter.join(map(str, line))}\n")

    result = list()
    current_session = Session()
    for i, link in enumerate(links):
        print(i)
        if i % 100 == 0:
            current_session = Session()
        response = current_session.get(link)
        soup = BeautifulSoup(response.text, 'lxml')
        nav_panel_list = soup.find_all(class_="pointNaviCont")
        for element in nav_panel_list:
            if element.find(class_="iconarchive") is not None:
                place = get_place(element.find("a")["href"])
                if [place, element.find("a")["href"], 0] not in result:
                    result.append([place, element.find("a")["href"], 0])
                    write_line(static_root, [place, element.find("a")["href"], 0], delimiter)
            elif element.find(class_="iconmetar") is not None:
                place = get_place(element.find("a")["href"])
                if [place, element.find("a")["href"], 1] not in result:
                    result.append([place, element.find("a")["href"], 1])
                    write_line(static_root, [place, element.find("a")["href"], 1], delimiter)
            elif element.find(class_="iconwug") is not None:
                place = get_place(element.find("a")["href"])
                if [place, element.find("a")["href"], 2] not in result:
                    result.append([place, element.find("a")["href"], 2])
                    write_line(static_root, [place, element.find("a")["href"], 2], delimiter)
        sleep(randint(1, 3))
    return result