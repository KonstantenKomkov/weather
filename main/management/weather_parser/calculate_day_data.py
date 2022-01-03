import ephem


# TODO: реализовать получение времени восхода и захода Солнца (сейчас нехватает часового пояса)
def calculate_day_length(latitude: float, longitude: float, date: datetime):
    """Function find sunrise, noon and sunset."""

    # utc_date = calculate_utc_russia(date)
    # Make an observer
    fred = ephem.Observer()

    # PyEphem takes and returns only UTC times. 15:00 is noon in Fredericton
    fred.date = "2021-06-21 00:00:00"

    # Location of place
    fred.lon = str(longitude)
    fred.lat = str(latitude)

    # Elevation of Fredericton, Canada, in metres
    fred.elev = 20

    # To get U.S. Naval Astronomical Almanac values, use these settings
    fred.pressure = 0
    fred.horizon = '-0:34'

    sunrise = fred.previous_rising(ephem.Sun())  # Sunrise
    noon = fred.next_transit(ephem.Sun(), start=sunrise)  # Solar noon
    sunset = fred.next_setting(ephem.Sun())  # Sunset
    print(f"{ephem.Date(sunrise)}, {ephem.Date(noon)}, {ephem.Date(sunset)}")
    return [sunrise, noon, sunset]
