import os
import logging
import re

import requests

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', datefmt='%d-%m-%y %H:%M:%S')
log = logging.getLogger('root')

# CONSTANT
WEATHER_KEY = os.environ.get('WEATHER_KEY')
API_URL = 'http://api.openweathermap.org/data/2.5/forecast?'


def main():
    """
    This is a program to get a 5-day weather forecast for any location speficied by the user
    User will be shown with the following information:
    - Date of the forecast
    - Time of the forecast
    - Description of the weather
    - Temperature of the weather
    - Wind Speed

    """
    if WEATHER_KEY is not None:
        # Get user input for the city and state of interest
        city, state = get_location()
        # Get the preferred unit of measurement from the user
        preferred_unit = get_unit()
        # Request the data from the API
        weather, errors = get_weather(city, state, preferred_unit)
        if weather is None:
            # print out a friendly message here for user to inform them failure in getting the data from the API
            print(f'Sorry there is an error in getting the forecast for {city.title()},{state.upper()}. Please try again later ')
        else:
            # Clean the data and store it in a dictionary format with day as key and the data for that day as value
            weather_obj = organize_data(weather)
            display_data(weather_obj, preferred_unit, city, state)

    else:
        # Choose to do logging here so the developer can see this error message
        log.error(f'WEATHER_KEY is {WEATHER_KEY}. Please set the environment variable before proceeding.')


def get_location(city=None, state=None):

    while city is None:
        city = input('What is the city that you would like to search for?  ').strip()
        # Validate if there is any city being provided and if they are alphabet
        # if not will print out a friendly message
        if len(city) <= 1 or not city.isalpha():
            print('Invalid input. Please enter a valid city name that is more than 1 characters.')
            city = None
        else:
            city = city.lower()

    while state is None and city is not None:
        tmp_city = city.title()
        state = input(f'What is the 2-letter country code for {tmp_city} city?  ').strip()
        # Validate if there is any state being provided and if they are alphabet
        # if not will print out a friendly message
        if len(state) != 2 or not state.isalpha():
            print('Invalid input. Please enter a valid country code that is 2-letter.')
            state = None
        else:
            state = state.lower()

    return city, state


def get_unit(unit=None):

    unit_list = ['standard', 'metric', 'imperial']

    while unit is None:
        unit = input('What unit of measurements do you preferred? standard(K), metric(C) or imperial(F)? ').strip()
        if unit.lower() not in unit_list:
            print(f'Invalid input. Please enter one of the following options: {unit[0], unit[1], unit[2]}')
            unit = None
        else:
            unit = unit.lower()
    return unit


def get_weather(city, state, unit):
    params = {'q': str(city) + ',' + str(state) + ',us', 'units': unit, 'appid': WEATHER_KEY}
    res = requests.get(API_URL, params=params)
    try:
        res.raise_for_status()  # Raise exception for 400 or 500 errors
        data = res.json()
        return data, None
    except Exception as e:
        # Use logger here to provided error message to the developer
        log.exception(f'Error occurred. More detail: {e}')
        log.exception(f'Error Message from request: {res.text}')
        return None, e


def organize_data(data):
    five_day_forecast = dict()

    counter = 0

    for interval in range(len(data['list'])):

        # It is 3 hours interval within the a day which is 8 data set per day
        if interval % 8 == 0:
            weather_info = list()
            dt_txt = data['list'][interval]['dt_txt']
            day = re.search(r'\d{4}-\d{2}-\d{2}', dt_txt).group(0)
            five_day_forecast.update({day: weather_info})
        # I choose to use the local time because I think it will be beneficial for the user that is looking up the weather for that location
        # So they can take note of the right time without worrying about converting the timezone difference.
        else:
            weather_data = list()
            tmp_time = data['list'][interval]['dt_txt']
            formatted_time = re.search(r'\d{2}:\d{2}:\d{2}', tmp_time).group(0)
            tmp_temp = data['list'][interval]['main']['temp']
            weather_description = data['list'][interval]['weather'][0]['description']
            tmp_wind = data['list'][interval]['wind']['speed']
            weather_data.append([formatted_time, tmp_temp, weather_description, tmp_wind])
            weather_info.append(weather_data)
            five_day_forecast.update({day: weather_info})

    return five_day_forecast


def display_data(data, unit, city, state):
    if unit == 'metric':
        tmp_unit = 'C'
        spd_unit = 'm/s'
    elif unit == 'imperial':
        tmp_unit = 'F'
        spd_unit = 'mph'
    else:
        tmp_unit = 'K'
        spd_unit = 'm/s'

    # Format the city and state string
    city = city.title()
    state = state.upper()

    print('\nHere is the weather forecast for the next 5 days with 3 hour step.\n')

    for day, weather in data.items():
        print(f'***** For {day} *****\n')
        for each in weather:
            print(f'At {each[0][0]}, the weather in {city},{state} will have {each[0][2]}\nTemperature: {each[0][1]} {tmp_unit}\nWind '
                  f'Speed: {each[0][3]} {spd_unit}\n')


if __name__ == "__main__":
    main()
