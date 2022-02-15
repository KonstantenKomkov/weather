Минимальные температуры по станциям и даты когда эти температуры были зафиксированы
```sql
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
```sql
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
```sql
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
```sql
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
Выборка минимальной и максимальной температуры, а также их дат по метеостанциям
```sql
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
	X.date as cold_date,
	X.temperature as min_temperature,
	Y.date as hot_date,
	Y.temperature as max_temperature
FROM X
INNER JOIN Y ON (X.weather_station_id = Y.weather_station_id)
WHERE X.num = 1 and Y.num = 1
```
Средние температуры по месяцам и годам
```sql
CREATE MATERIALIZED VIEW avg_month_temperature_by_month_and_year AS (
	WITH X AS (
		SELECT
			a.weather_station_id,
			AVG(a.temperature) as avg_day_temperature,
			EXTRACT(MONTH FROM a.date::date) as num_month,
			EXTRACT(YEAR FROM a.date::date) as num_year
		FROM
			weather a
		GROUP BY
			a.date::date,
			a.weather_station_id)
	SELECT
		X.weather_station_id,
		AVG(X.avg_day_temperature) as avg_month_temperature,
		X.num_month,
		X.num_year
	FROM X
	GROUP BY
		X.weather_station_id,
		X.num_month,
		X.num_year
	ORDER BY
		X.weather_station_id,
		X.num_month,
		X.num_year)
```
Средняя температура по месяцам и их количество
```sql
CREATE MATERIALIZED VIEW avg_month_temperatures AS (
	WITH Y AS (
		WITH X AS (
			SELECT
				a.weather_station_id,
				AVG(a.temperature) as avg_day_temperature,
				EXTRACT(MONTH FROM a.date::date) as num_month,
				EXTRACT(YEAR FROM a.date::date) as num_year
			FROM
				weather a
			GROUP BY
				a.date::date,
				a.weather_station_id)
		SELECT
			X.weather_station_id,
			AVG(X.avg_day_temperature) as avg_month_temperature,
			X.num_month,
			X.num_year
		FROM X
		GROUP BY
			X.weather_station_id,
			X.num_month,
			X.num_year
		ORDER BY
			X.weather_station_id,
			X.num_month,
			X.num_year)
	SELECT
		Y.weather_station_id,
		AVG(Y.avg_month_temperature) as avg_all_unique_month_temperature,
		Y.num_month,
		COUNT(Y.num_month) as count_of_observations
	FROM Y
	GROUP BY
		Y.weather_station_id,
		Y.num_month)
```