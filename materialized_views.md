Минимальные температуры по станциям и даты когда эти температуры были зафиксированы
```buildoutcfg
CREATE MATERIALIZED VIEW min_temperatures AS (
	WITH X AS (
		SELECT
			a.weather_station_id,
			a.date,
			a.temperature,
			RANK() OVER (PARTITION BY a.weather_station_id ORDER BY a.temperature ASC) as num
		FROM
			weather a
		WHERE
			a.temperature IS NOT NULL)
	SELECT
		X.weather_station_id, X.date, X.temperature
	FROM X
	WHERE X.num = 1
	ORDER BY
		X.weather_station_id)
```
Максимальные температуры по станциям и даты когда эти температуры были зафиксированы
```buildoutcfg
CREATE MATERIALIZED VIEW max_temperatures AS (
	WITH X AS (
		SELECT
			a.weather_station_id,
			a.date,
			a.temperature,
			RANK() OVER (PARTITION BY a.weather_station_id ORDER BY a.temperature DESC) as num
		FROM
			weather a
		WHERE
			a.temperature IS NOT NULL)
	SELECT
		X.weather_station_id, X.date, X.temperature
	FROM X
	WHERE X.num = 1
	ORDER BY
		X.weather_station_id)
```
Выбор только одной даты с минимальной температурой по станции
```buildoutcfg
WITH X AS (
	SELECT
		a.weather_station_id,
		a.date,
		a.temperature,
		ROW_NUMBER() OVER (PARTITION BY a.weather_station_id) as num
	FROM min_temperatures a)
SELECT 
	X.weather_station_id,
	X.date,
	X.temperature
FROM X
WHERE X.num = 1
```
Выбор только одной даты с максимальной температурой по станции
```buildoutcfg
WITH X AS (
	SELECT
		a.weather_station_id,
		a.date,
		a.temperature,
		ROW_NUMBER() OVER (PARTITION BY a.weather_station_id) as num
	FROM max_temperatures a) 
SELECT 
	X.weather_station_id,
	X.date,
	X.temperature
FROM X
WHERE X.num = 1
```
Выборка минимальной и максимальной температуры а также их дат по метеостанциям
```buildoutcfg
WITH X AS (
	SELECT
		a.weather_station_id,
		a.date,
		a.temperature,
		ROW_NUMBER() OVER (PARTITION BY a.weather_station_id) as num
	FROM min_temperatures a),
Y AS (
	SELECT
		a.weather_station_id,
		a.date,
		a.temperature,
		ROW_NUMBER() OVER (PARTITION BY a.weather_station_id) as num
	FROM max_temperatures a) 
SELECT 
	X.weather_station_id,
	X.date,
	X.temperature as min_temperature,
	Y.date,
	Y.temperature as max_temperature
FROM X
INNER JOIN Y ON (X.weather_station_id = Y.weather_station_id)
WHERE X.num = 1 and Y.num = 1
```