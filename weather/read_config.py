import configparser
from app_models import App, Database, Yandex


def try_parse(value: str) -> int | bool:
    try:
        return int(value)
    except ValueError:
        return False


def read_config() -> App:
    config = configparser.ConfigParser()
    config.read("config.ini")
    return App(
        secret_key=config["app"]["secret_key"],
        database=Database(
            engine=config["db"]["engine"],
            name=config["db"]["database"],
            user=config["db"]["user"],
            password=config["db"]["password"],
            host=config["db"]["host"],
            port=config["db"]["port"],),
        # Replace in config every time when you need update your sources
        yandex=Yandex(
            login=config["yandex"]["login"],
            password=config["yandex"]["pass"],
            api_key=config["yandex"]["api_key"],
            token=config["yandex"]["token"],
            id=config["yandex"]["id"],),)
