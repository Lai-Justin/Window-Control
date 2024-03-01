# from pigps import GPS
import requests
import datetime
import socket 
import Adafruit_DHT as dht 
from datetime import datetime
from time import sleep, strftime, time
import sys



# APIs
weatherAPI = "https://api.weather.gov"
geoLocationAPI = 'https://api.ipgeolocation.io/ipgeo?apiKey='
ipGeoLocationKey = 'c868e38236c84faa9c10162a3e5f2a7f'
IPAddr = 0

# Initialize Latitude and Longitude
currentLat = 0
currentLong = 0

# Retrieves the IP address
def getIp():
    hostname=socket.gethostname()   
    IPAddr=socket.gethostbyname(hostname)  
    print(IPAddr)
    return IPAddr

# Retrieves the latitude and longitude based on IP
def getGeoLocation():
    response = requests.get(f"{geoLocationAPI}{ipGeoLocationKey}&{IPAddr}")
    response = response.json()
    currentLat = response["latitude"]
    currentLong = response["longitude"]
    print(currentLat, currentLong)
    return currentLat, currentLong

# Retrives the Weather based on longitude and latitude
def weather(latitude, longitude):
    response = requests.get(f"{weatherAPI}/points/{latitude},{longitude}")
    response = response.json()
    link = response["properties"]['forecastHourly']
    response = requests.get(link)
    forecast = response.json()
    print(forecast['properties']['periods'][1])
    return forecast['properties']['periods'][1]

# takes the json returned from weather to find temperature (Celsius)
def temperature(data):
    temp = data['temperature']
    print(temp)

# takes the json returned from weather to find rain percentage
def rainPercentage(data):
    percent = data['probabilityOfPrecipitation']['value']
    print(percent)

# takes the json returned from weather to find wind speed
def windSpeed(data):
    wind = data['windSpeed']
    print(wind)


while(True):
    input = int(sys.stdin.readline().strip())
    if input == 1:
        IPAddr = getIp()
    if input == 2:
        currentLat, currentLong = getGeoLocation()
    if input == 3:
        data = weather(currentLat, currentLong)
    if input == 4:
        temperature(data)
    if input == 5:
        rainPercentage(data)
    if input == 6:
        windSpeed(data)












"""
# Set latitude and longitude based on IP
currentLat, currentLong = getGeoLocation()
# Get weather and set it to weather_JSON
weather_JSON = weather(currentLat, currentLong)

DHT = 4
# Converts the temperature from Celsius to Fahrenheit
def convert_temp(num):
    return num * (9 / 5) + 32

# Logs the temperature from temperature sensor and weather API
# to a csv called temperature_log_api.csv
while(True):
    interiorhumidity, interiortemp = dht.read_retry(dht.DHT11, DHT)
    interiortemp = convert_temp(interiortemp)
    weather_JSON = weather(currentLat, currentLong)
    with open("temperature_log_api.csv", "a") as log:
        log.write("{0},{1},{2}\n".format(strftime("%Y-%m-%d %H:%M:%S"),temperature(weather_JSON),str(interiortemp)))
        sleep(10)
# can close the window based off of wind speed or precipitation values

maxWindSpeed = 25
maxPrecipChance = 40


'''while(True):
    # probably do it based on temperature first, but check windSpeed
    # don't want it to be too windy
    # also check rain?
    
    if (weather(IVLat, IVLong)['windSpeed'] > maxWindSpeed):
        if(windowStatus == True):
            motor.backward()
            sleep(5)
            motor.stop()
    
    if (weather(IVLat, IVLong)['probabilityOfPrecipitation']['value']> maxPrecipChance):
        if(windowStatus == True):
            motor.backward()
            sleep(5)
            motor.stop()'''

"""

