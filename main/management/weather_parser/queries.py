def insert_csv_weather_station_data(my_path: str, delimiter: str) -> str:
    return "COPY weather (weather_station_id, \"date\", temperature, pressure, pressure_converted, baric_trend, " \
           "humidity, wind_direction_id, wind_speed, max_wind_speed, max_wind_speed_between, cloud_cover_id, " \
           "current_weather, past_weather, past_weather_two, min_temperature, max_temperature, cloud_cl, " \
           "cloud_count_id, cloud_hight, cloud_cm, cloud_three, visibility, dew_point, rainfall, rainfall_time, " \
           "soil_condition, soil_temperature, soil_with_snow, snow_hight) FROM '%(my_path)s' DELIMITER " \
           "'%(delimiter)s' NULL AS 'null' CSV HEADER;" % {"my_path": my_path, "delimiter": delimiter}


def insert_csv_metar_data(my_path: str, delimiter: str) -> str:
    return "COPY weather (weather_station_id, \"date\", temperature, pressure, pressure_converted, humidity, " \
           "wind_direction_id, wind_speed, max_wind_speed, current_weather, past_weather, cloud_cover_id, " \
           "visibility, dew_point) FROM '%(my_path)s' DELIMITER " \
           "'%(delimiter)s' NULL AS 'null' CSV HEADER;" % {"my_path": my_path, "delimiter": delimiter}
