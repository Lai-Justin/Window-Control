from gpiozero import Button
import time
from time import sleep, strftime, time
from gpiozero import Motor
from gpiozero import MCP3008
from gpiozero import Motor
import RPi.GPIO as GPIO
import requests
from datetime import datetime
import jsonlines
import Adafruit_DHT as dht
import socket 
from weatherAPI import getGeoLocation, getIp, weather
# pin that data is being read from on pi
DHT = 4

f = open("temperatures.jsonl", "a")

readingIntervals = 1800
# readingIntervals = 10
maxTemperature = 80
maxHumidity = 70
adc = MCP3008(channel=0)
currTemperature = 0
#windowStatus = False 
motor = Motor(17, 18)
percentOpen = 50

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

# Retrieves the latitude and longitude based on IP
def getGeoLocation():
    response = requests.get(f"{geoLocationAPI}{ipGeoLocationKey}&{IPAddr}")
    response = response.json()
    currentLat = response["latitude"]
    currentLong = response["longitude"]
    return currentLat,currentLong

# Retrives the Weather based on longitude and latitude
def weather(latitude, longitude):
    response = requests.get(f"{weatherAPI}/points/{latitude},{longitude}")
    response = response.json()
    link = response["properties"]['forecastHourly']
    response = requests.get(link)
    forecast = response.json()
    return forecast['properties']['periods'][1]

# takes the json returned from weather to find temperature (Celsius)
def temperature(data):
    temp = data['temperature']
    return temp

# takes the json returned from weather to find rain percentage
def rainPercentage(data):
    percent = data['probabilityOfPrecipitation']['value']
    return percent

# takes the json returned from weather to find wind speed
def windSpeed(data):
    wind = data['windSpeed']
    return wind


# Set latitude and longitude based on IP
currentLat, currentLong = getGeoLocation()
# Get weather and set it to weather_JSON
weather_JSON = weather(currentLat, currentLong)

DHT = 4
# Converts the temperature from Celsius to Fahrenheit
def convert_temp(num):
    return num * (9 / 5) + 32


# for motor information now
# inputs for motor
in1 = 17
in2 = 18
in3 = 27
in4 = 22

# don't change step_sleep too low
step_sleep = 0.002
step_count = 4096 
# direction = False # T for CW, F for CCW

# for the lights
step_sequence = [[1,0,0,1],
                 [1,0,0,0],
                 [1,1,0,0],
                 [0,1,0,0],
                 [0,1,1,0],
                 [0,0,1,0],
                 [0,0,1,1],
                 [0,0,0,1]]

# setting up motor stuff 
GPIO.setmode( GPIO.BCM )
GPIO.setup( in1, GPIO.OUT )
GPIO.setup( in2, GPIO.OUT )
GPIO.setup( in3, GPIO.OUT )
GPIO.setup( in4, GPIO.OUT )

# initializes
GPIO.output( in1, GPIO.LOW )
GPIO.output( in2, GPIO.LOW )
GPIO.output( in3, GPIO.LOW )
GPIO.output( in4, GPIO.LOW )
    
motor_pins = [in1,in2,in3,in4]
motor_step_counter = 0

def cleanup():
    GPIO.output( in1, GPIO.LOW )
    GPIO.output( in2, GPIO.LOW )
    GPIO.output( in3, GPIO.LOW )
    GPIO.output( in4, GPIO.LOW )
    GPIO.cleanup()

def move_motor(directions):
    try:
        i = 0
        for i in range(step_count):
            for pin in range(0, len(motor_pins)):
                GPIO.output( motor_pins[pin], step_sequence[motor_step_counter][pin] )
            if directions == True:
                motor_step_counter = (motor_step_counter - 1) % 8
            elif directions==False:
                motor_step_counter = (motor_step_counter + 1) % 8
            time.sleep( step_sleep )
    except KeyboardInterrupt:
        cleanup()
        exit( 1 )


while(True):
    # all temperature is in Fahrenheit
    motor(True)
    interiorhumidity, interiortemp = dht.read_retry(dht.DHT11, DHT)
    interiortemp = convert_temp(interiortemp)
    weather_JSON = weather(currentLat, currentLong)
    with open("temperature_log_api.csv", "a") as log:
        log.write("{0},{1},{2}\n".format(strftime("%Y-%m-%d %H:%M:%S"),temperature(weather_JSON),str(interiortemp)))
        # make sure to change sleep time
        sleep(10)
    
    # Based on the temp
    # if hot then close or open?
    # make sure it is not raining
    # maybe before motor activation check outdoor temp to make sure it is cooler
    
    
    # checks if indoor temp is hotter than what we think is hot
    if(interiortemp > maxTemperature):
        # check if indoor temp is hotter than outdoors and not raining
        if(interiortemp > temperature(weather_JSON) and rainPercentage(weather_JSON) < 10):
            # check that window is open fully (if the window is not already fully open, open the window)
            if percentOpen < 100:
            #if(windowStatus == False):
                move_motor(True)
                sleep(5)
                percentOpen += 5
                
    else:
        # check that window is not closed fully
        # if the window can still be closed, close it
        #if(windowStatus == True):
        if percentOpen > 0:
            move_motor(False)
            sleep(5)
            percentOpen -= 5
     
    
    #f.write(tmp)
    # f.write({"temperature": interiortemp, "timestamp": datetime.now().timestamp()})
    

    # close the window if it is raining
    if (rainPercentage(weather_JSON) > 70):
        # close the window completely
        #while (windowStatus == True):
        while percentOpen > 0:
            move_motor(False)
            #direction = True
            sleep(5)
            percentOpen -= 5
    
    cleanup()
    sleep(readingIntervals)
