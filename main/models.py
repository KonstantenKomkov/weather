from django.db import models


# General cloud cover
class Cloudiness(models.Model):
    description = models.CharField(unique=True, max_length=350, verbose_name='общая облачность',)
    scale = models.IntegerField(blank=True, null=True, verbose_name='градация',)

    class Meta:
        db_table = 'cloudiness'
        verbose_name = 'общая облачность'
        verbose_name_plural = 'общая облачность'


# The number of all observed Cl clouds or, in the absence of Cl clouds, the number of all observed Cm clouds
class CloudinessCl(models.Model):
    description = models.CharField(max_length=100, verbose_name='общая облачность', unique=True,)
    scale = models.IntegerField(blank=True, null=True, verbose_name='градация',)

    class Meta:
        db_table = 'cloudiness_cl'
        verbose_name = 'процент наблюдающихся облаков'
        verbose_name_plural = 'процент наблюдающихся облаков'


class WindDirection(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='направление ветра (румбы) на высоте 10 - 12 м над земной поверхностью, осреднённое за '
                     '10-минутный период, непосредственно предшествующий сроку наблюдения', unique=True,)

    class Meta:
        db_table = 'wind_directions'
        verbose_name = 'направление ветра'
        verbose_name_plural = 'направления ветра'


class Country(models.Model):
    name = models.CharField(max_length=50, null=False, verbose_name='название',)

    class Meta:
        db_table = 'countries'
        verbose_name = 'страна'
        verbose_name_plural = 'страны'


class Region(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name='страна',)
    name = models.CharField(max_length=255, null=False, verbose_name='название', unique=True,)

    class Meta:
        db_table = 'regions'
        verbose_name = 'регион'
        verbose_name_plural = 'регионы'


class Place(models.Model):
    name = models.CharField(max_length=70, verbose_name='место',)
    latitude = models.FloatField(verbose_name='широта',)
    longitude = models.FloatField(verbose_name='долгота',)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='регион', null=True,)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name='страна',)

    class Meta:
        db_table = 'places'
        verbose_name = 'название места'
        verbose_name_plural = 'названия мест'
        unique_together = ('country', 'region', 'name',)


class WeatherStationType(models.Model):
    type = models.CharField(unique=True, max_length=50, verbose_name='метеостанция, METAR, метеодатчик',)

    class Meta:
        db_table = 'weather_station_type'
        verbose_name = 'тип метеостанции'
        verbose_name_plural = 'типы метеостанций'


class WeatherStation(models.Model):
    number = models.CharField(unique=True, max_length=10, verbose_name='идентификатор',)
    rp5_link = models.CharField(max_length=255, verbose_name='ссылка на метеостанцию, rp5',)
    start_date = models.DateField(blank=True, null=True, verbose_name='дата начала наблюдений',)
    last_date = models.DateField(blank=True, null=True, verbose_name='дата последней загрузки',)
    type = models.ForeignKey(WeatherStationType, on_delete=models.CASCADE, blank=True, null=True, verbose_name='тип',)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, blank=True, null=True, verbose_name='место',)
    metar = models.IntegerField(null=True, verbose_name='metar параметр для запроса',)

    class Meta:
        db_table = 'weather_stations'
        verbose_name = 'метеостанция'
        verbose_name_plural = 'метеостанции'

    def to_csv(self, delimiter):
        return f"{self.place.name}{delimiter}{self.rp5_link}{delimiter}{self.type}{delimiter}" \
               f"{'None' if self.last_date is None else self.last_date.strftime('%Y-%m-%d')}" \
               f"{delimiter}{self.number}{delimiter}{self.place.country.name}{delimiter}{self.pk}{delimiter}" \
               f"{self.place.latitude}{delimiter}{self.place.longitude}{delimiter}{self.metar}{delimiter}" \
               f"{'None' if self.start_date is None else self.start_date.strftime('%Y-%m-%d')}"


# Data from the weather station
class Weather(models.Model):
    date = models.DateTimeField(verbose_name='дата и время',)
    temperature = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True,
        verbose_name='температура воздуха, (°С) на высоте 2 м над поверхностью земли',)
    pressure = models.DecimalField(
        max_digits=4, decimal_places=1, blank=True, null=True,
        verbose_name='атмосферное давление на уровне станции (миллиметры ртутного столба)',)
    pressure_converted = models.DecimalField(
        max_digits=4, decimal_places=1, blank=True, null=True,
        verbose_name='атмосферное давление, приведённое к среднему уровню моря (миллиметры ртутного столба)',)
    baric_trend = models.DecimalField(
        max_digits=4, decimal_places=1, blank=True, null=True,
        verbose_name='барическая тенденция: изменение атмосферного давления за последние 3 часа (миллиметры ртутного '
                     'столба)',)
    humidity = models.IntegerField(
        blank=True, null=True, verbose_name='относительная влажность (%) на высоте 2 м над поверхностью земли',)
    wind_speed = models.IntegerField(
        blank=True, null=True,
        verbose_name='скорость ветра на высоте 10-12 м над земной поверхностью, осреднённая за 10-минутный период, '
                     'непосредственно предшествующий сроку наблюдения (метры в секунду)',)
    max_wind_speed = models.IntegerField(
        blank=True, null=True,
        verbose_name='максимальное значение порыва ветра на высоте 10-12 метров над земной поверхностью за 10-минутный '
                     'период, непосредственно предшествующий сроку наблюдения (метры в секунду)',)
    max_wind_speed_between = models.IntegerField(
        blank=True, null=True,
        verbose_name='максимальное значение порыва ветра на высоте 10-12 метров над земной поверхностью за период '
                     'между сроками (метры в секунду)',)
    current_weather = models.TextField(
        blank=True, null=True, verbose_name='текущая погода, сообщаемая с метеорологической станции',)
    past_weather = models.CharField(
        max_length=255, blank=True, null=True, verbose_name='прошедшая погода между сроками наблюдения 1',)
    past_weather_two = models.CharField(max_length=255, blank=True, null=True,
                                        verbose_name='прошедшая погода между сроками наблюдения 2',)
    min_temperature = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True,
        verbose_name='минимальная температура воздуха (°С) за прошедший период (не более 12 часов)',)
    max_temperature = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True,
        verbose_name='максимальная температура воздуха (°С) за прошедший период (не более 12 часов)',)
    cloud_cl = models.CharField(max_length=255, blank=True, null=True,
                                verbose_name='слоисто-кучевые, слоистые, кучевые и кучево-дождевые облака (Cl)',)
    cloud_hight = models.CharField(
        max_length=255, blank=True, null=True, verbose_name='высота основания самых низких облаков (м)',)
    cloud_cm = models.CharField(max_length=255, blank=True, null=True,
                                verbose_name='высококучевые, высокослоистые и слоисто-дождевые облака (Cm)',)
    cloud_three = models.CharField(
        max_length=255, blank=True, null=True, verbose_name='перистые, перисто-кучевые и перисто-слоистые облака',)
    visibility = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True, verbose_name='горизонтальная дальность видимости (км)',)
    dew_point = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True,
        verbose_name='температура точки росы на высоте 2 метра над поверхностью земли (°С)',)
    rainfall = models.CharField(max_length=50, blank=True, null=True, verbose_name='количество выпавших осадков (мм)',)
    rainfall_time = models.IntegerField(
        blank=True, null=True, verbose_name='период времени за который накоплено указанное количество осадков (часы)',)
    soil_condition = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name='состояние поверхности почвы без снега или измеримого ледяного покрова',)
    soil_temperature = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True,
        verbose_name='минимальная температура поверхности почвы за ночь (°С)',)
    soil_with_snow = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name='состояние поверхности почвы со снегом или измеримым ледяным покровом',)
    snow_hight = models.CharField(max_length=255, blank=True, null=True, verbose_name='высота снежного покрова (см)',)
    cloud_count = models.ForeignKey(
        CloudinessCl, on_delete=models.CASCADE, null=True,
        verbose_name='количество всех наблюдающихся облаков Cl или, при отсутствии облаков Cl, количество всех '
                     'наблюдающихся облаков Cm',)
    cloud_cover = models.ForeignKey(
        Cloudiness, on_delete=models.CASCADE, blank=True, null=True, verbose_name='общая облачность (%)',)
    weather_station = models.ForeignKey(WeatherStation, on_delete=models.CASCADE, verbose_name='метеостанция',)
    wind_direction = models.ForeignKey(
        WindDirection, on_delete=models.CASCADE, blank=True, null=True,
        verbose_name='направление ветра (румбы) на высоте 10 - 12 м над земной поверхностью, осреднённое за '
                     '10-минутный период, непосредственно предшествующий сроку наблюдения',)

    class Meta:
        db_table = 'weather'
        verbose_name = 'погода'
        verbose_name_plural = 'погода'
        unique_together = (('weather_station', 'date'),)
