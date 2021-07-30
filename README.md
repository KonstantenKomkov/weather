Weather parser for site [rp5.ru][1]
========================
About
-------------------------
Parser worked in two modes:
- getting data from the date of start observations;
- getting data for missing period (it is assumed to download from a specific date).

Parser get weather data for your weather stations for years. That data converted for loading to database.
Database structure described in models.py file. Aim of getting weather data might be a lot:
- climate change studies,
- agricaltural expiriments,
- comparison of resort areas, etc...

How to use
-------------------------
Now cities.csv contain data of my last parsing. For clear it use:
```//Django command:
python manage.py clear_cities
```
Clear_cities command delete all exept place, link, and weather station type.
```//Django command:
python manage.py get_weather
```

Open config.example.ini and write connection to your postgresql database or don't do it if you want to save data in csv files.
Write folder path for saving data it is necessarily. Delete .example from config name. If you want use another database check how to make it with [pyDAL][2].
Parser work with csv file (cities.csv) with 3 required parameters:  
- city name (maybe place name);
- link on rp5 site page with that city or place;
- type of data: 0 - weather station, 1 - METAR, 2 - weather sensor;  
  
and optional parameters (parser add it autonomous):
- last date of download data (yesterday);
- number of weather station;
- country;
- id weather station if you are using database;
- latitude weather station;
- longitude weather station;
- metar (0 if SYNOP/ value if metar).

[Cities.csv][3] contain some data as example. Put your data here.
[places.txt][4] contain all weather sources for Russia at date 17.07.2021.

If you want to find weather sources for other countries use:
```//Django command:
python manage.py find_sources REQUIRED_YOUR_LINK
```

That command find all weather sources but you need add link. Example for Russia:
```//Django command:
python manage.py find_sources https://rp5.ru/Погода_в_России
```
After that you should start:
```//Django command:
python manage.py update_sources
```
for cities.csv file contain unique links of your finded stations.

How to use Yandex API
-------------------------
Find main -> example directory and change {your_api_key} in reverse_geocode.html. Open than file in browser. And copy token, id to config.ini, you find that in developers settings -> network -> JS -> click on the map for callback -> Request URL string will contain token and id. Also you need to add your login (everything up to the symbol @ in your yandex email) and password.

[1]: https://rp5.ru/Погода_в_мире                                                                            "rp5.ru"
[2]: http://web2py.com/books/default/chapter/29/06/the-database-abstraction-layer                            "pyDAL"
[3]: https://github.com/KonstantenKomkov/rp5_weather/blob/master/static/cities.txt                           "cities.csv"
[4]: https://github.com/KonstantenKomkov/weather/blob/master/main/management/weather_stations_csv/places.txt "places.txt"
