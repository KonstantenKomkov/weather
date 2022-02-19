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
Функция выбора средних значений количества дней и температур за всё время наблюдений, которые больше указанной нами температуры.
```sql
CREATE OR REPLACE FUNCTION get_avg_days_and_temperatures_for_years (in more_than numeric)
RETURNS table (weather_station_id bigint,
			   avg_days numeric,
			   avg_temperature numeric,
			   count_years bigint)
AS $$
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
			COUNT(X.avg_day_temperature) as day_with_plus_temperature,
			ROUND(SUM(X.avg_day_temperature), 1) as sum_plus_temperature_for_year,
			X.num_year
		FROM X
		WHERE X.avg_day_temperature > more_than and X.num_year != date_part('year', CURRENT_DATE)
		GROUP BY
			X.weather_station_id,
			X.num_year
		ORDER BY
			X.weather_station_id,
			X.num_year)
	SELECT
		Y.weather_station_id,
		ROUND(AVG(Y.day_with_plus_temperature)) as avg_day_with_plus_temperature,
		ROUND(AVG(Y.sum_plus_temperature_for_year), 1) as avg_sum_plus_temperature_for_years,
		COUNT(Y.num_year)
	FROM Y
	GROUP BY
		Y.weather_station_id;
$$
LANGUAGE sql;
```
Среднее количество дней с положительной температурой и средняя сумма положительных температур за год за весь период наблюдений
```sql
CREATE MATERIALIZED VIEW avg_days_and_sum_plus_temperature_for_year AS (
	SELECT
		weather_station_id,
		avg_days,
		avg_temperature,
		count_years
	FROM get_avg_days_and_temperatures_for_years(0))
```
Среднее количество дней с положительной температурой больше 10 градусов и средняя сумма этих температур за год за весь период наблюдений
```sql
CREATE MATERIALIZED VIEW avg_days_and_sum_active_temperatures_for_years AS (
	SELECT
		weather_station_id,
		avg_days,
		avg_temperature,
		count_years
	FROM get_avg_days_and_temperatures_for_years(10))
```
Усредненные показатели температур для сельского хозяйства
```sql
CREATE MATERIALIZED VIEW agro_temperature_indicators AS (
	WITH X AS (
	SELECT
		e.weather_station_id,
		e.avg_all_unique_month_temperature as avg_january_temperature_for_years
	FROM
		avg_month_temperatures e
	WHERE e.num_month = 1),
	Y AS (
		SELECT
		e.weather_station_id,
		e.avg_all_unique_month_temperature as avg_july_temperature_for_years
	FROM
		avg_month_temperatures e
	WHERE e.num_month = 7)
	SELECT
		a.weather_station_id,
		a.date as min_temperature_date,
		a.temperature as min_temperature,
		b.temperature as max_temperature,
		b.date as max_temperature_date,
		c.avg_days as avg_days_with_plas_temperature_for_year,
		c.avg_temperature as avg_sum_plus_temperature_for_year,
		c.count_years,
		d.avg_days as avg_days_with_active_temperature_for_year,
		d.avg_temperature as avg_sum_active_temperature_for_year,
		X.avg_january_temperature_for_years,
		Y.avg_july_temperature_for_years
	FROM
		min_temperatures a
		INNER JOIN max_temperatures b ON (a.weather_station_id = b.weather_station_id)
		INNER JOIN avg_days_and_sum_plus_temperature_for_year c ON (a.weather_station_id = c.weather_station_id)
		INNER JOIN avg_days_and_sum_active_temperatures_for_years d ON (a.weather_station_id = d.weather_station_id)
		INNER JOIN X ON (a.weather_station_id = X.weather_station_id)
		INNER JOIN Y ON (a.weather_station_id = Y.weather_station_id))
```