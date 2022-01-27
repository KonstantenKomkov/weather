def insert_wind_data():
    return "INSERT INTO wind_directions (\"name\") VALUES ('Ветер, дующий с юга'), ('Ветер, дующий с юго-востока'), " \
           "('Ветер, дующий с востока'), ('Штиль, безветрие'), ('Ветер, дующий с юго-юго-востока'), " \
           "('Ветер, дующий с северо-востока'), ('Ветер, дующий с северо-северо-востока'), " \
           "('Ветер, дующий с западо-северо-запада'), ('Ветер, дующий с северо-северо-запада'), " \
           "('Ветер, дующий с востоко-северо-востока'), ('Ветер, дующий с юго-запада'), " \
           "('Ветер, дующий с юго-юго-запада'), ('Ветер, дующий с западо-юго-запада'), ('Ветер, дующий с запада'), " \
           "('Ветер, дующий с северо-запада'), ('Ветер, дующий с севера'), ('Ветер, дующий с востоко-юго-востока'), " \
           "('Переменное направление')"


def insert_cloudiness_data():
    return "INSERT INTO cloudiness (description, scale) VALUES ('Облаков нет', 0), ('10%  или менее, но не 0', 1), " \
           "('20–30', 2), ('40', 3), ('50', 4), ('60', 5), ('70 – 80', 6), ('90  или более, но не 100%', 7), " \
           "('100', 8), ('Небо не видно из-за тумана и/или других метеорологических явлений.', null)"


def insert_cloudiness_cl_data():
    return "INSERT INTO cloudiness_cl (description, scale) VALUES ('Облаков нет', 0), ('10%  или менее, но не 0', 1)," \
           "('20–30', 2), ('40', 3), ('50', 4), ('60', 5), ('70 – 80', 6), ('90  или более, но не 100%', 7), " \
           "('100', 8), ('нет данных', null), " \
           "('Небо не видно из-за тумана и/или других метеорологических явлений.', null)"


def insert_csv_weather_station_data(my_path: str, delimiter: str) -> str:
    return "COPY weather (weather_station_id, \"date\", temperature, pressure, pressure_converted, baric_trend, " \
           "humidity, wind_direction_id, wind_speed, max_wind_speed, max_wind_speed_between, cloud_cover_id, " \
           "current_weather, past_weather, past_weather_two, min_temperature, max_temperature, cloud_cl, " \
           "cloud_count_id, cloud_hight, cloud_cm, cloud_three, visibility, dew_point, rainfall, rainfall_time, " \
           "soil_condition, soil_temperature, soil_with_snow, snow_hight) FROM '%(my_path)s' DELIMITER " \
           "'%(delimiter)s' NULL AS 'null' CSV HEADER;" % {'my_path': my_path, 'delimiter': delimiter}


def insert_csv_metar_data(my_path: str, delimiter: str) -> str:
    return "COPY weather (weather_station_id, \"date\", temperature, pressure, pressure_converted, humidity, " \
           "wind_direction_id, wind_speed, max_wind_speed, current_weather, past_weather, cloud_cover_id, " \
           "visibility, dew_point) FROM '%(my_path)s' DELIMITER " \
           "'%(delimiter)s' NULL AS 'null' CSV HEADER;" % {'my_path': my_path, 'delimiter': delimiter}
