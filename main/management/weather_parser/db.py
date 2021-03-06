from pydal import DAL, Field
from weather.settings import app


db = DAL(f'postgres://{app.database.user}:{app.database.password}@{app.database.host}/'
         f'{app.database.name}', migrate=False)

db.define_table('countries', Field('name', length=50, rname='"name"'),)
db.define_table('regions', Field('name', length=50, rname='"name"'),
                Field('country_id', 'reference countries', ondelete='CASCADE'),)
db.define_table('places', Field('name', length=50, rname='"name"'),
                Field('country_id', 'reference countries', ondelete='CASCADE'),
                Field('region_id', 'reference regions', ondelete='CASCADE'), Field('latitude', 'double'),
                Field('longitude', 'double'),)
db.define_table('weather_station_type', Field('type', length=50, rname='"type"'),)
db.define_table('weather_stations', Field('number', length=10,), Field('rp5_link', length=255),
                Field('last_date', 'date'), Field('place_id', 'referense places', ondelete='CASCADE'),
                Field('metar', 'integer'), Field('start_date', 'date'),
                Field('type_id', 'reference weather_station_type', ondelete='CASCADE'),)
db.define_table('wind_directions', Field('name', length=50))
db.define_table('cloudiness', Field('description', length=100), Field('scale', 'integer'))
db.define_table('cloudiness_cl', Field('description', length=100), Field('scale', 'integer'))
# Fields 'date' and 'weather_station_id' must be unique
# For postgresql: CREATE UNIQUE INDEX weather_station_and_datetime_unq ON weather (weather_station_id, "date");
db.define_table('weather', Field('weather_station_id', 'reference weather_stations', ondelete='CASCADE'),
                Field('temperature', 'decimal(3,1)'), Field('pressure', 'decimal(4,1)'),
                Field('pressure_converted', 'decimal(4,1)'), Field('baric_trend', 'decimal(4,1)'),
                Field('humidity', 'integer'), Field('wind_direction_id', 'reference wind_directions'),
                Field('wind_speed', 'integer'), Field('max_wind_speed', 'integer'),
                Field('max_wind_speed_between', 'integer'), Field('cloud_cover_id', 'reference cloudiness'),
                Field('current_weather', 'text'), Field('past_weather', length=255),
                Field('past_weather_two', length=255), Field('min_temperature', 'decimal(3,1)'),
                Field('max_temperature', 'decimal(3,1)'), Field('cloud_cl', length=255),
                Field('cloud_count_id', 'reference cloudiness_cl'), Field('cloud_hight', length=255),
                Field('cloud_cm', length=255), Field('cloud_three', length=255), Field('visibility', 'decimal(3,1)'),
                Field('dew_point', 'decimal(3,1)'), Field('rainfall', length=50), Field('rainfall_time', 'integer'),
                Field('soil_condition', length=255), Field('soil_temperature', 'decimal(3,1)'),
                Field('soil_with_snow', length=255), Field('snow_hight', length=255),
                Field('date', 'datetime', rname='"date"'))
