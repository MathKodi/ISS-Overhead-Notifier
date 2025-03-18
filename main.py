import requests
from datetime import datetime
import smtplib
import time
from dotenv import load_dotenv
import os

load_dotenv()

MY_EMAIL = os.getenv("MY_EMAIL")
MY_PASSWORD = os.getenv("PASSWORD")
LOCAL_UTC_OFFSET = -3
MY_LAT = 21.684950
MY_LONG = -51.074371

def utc_to_local(utc_hour):
    utc_hour += LOCAL_UTC_OFFSET
    if LOCAL_UTC_OFFSET > 0:
        if utc_hour > 23:
            utc_hour -= 24
    elif LOCAL_UTC_OFFSET < 0:
        if utc_hour < 0:
            utc_hour += 24
    return utc_hour

def is_isss_overhead():
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()

    data = response.json()

    longitude = float(data["iss_position"]["longitude"])
    latitude = float(data["iss_position"]["latitude"])
    if MY_LAT-5 <= latitude <= MY_LAT+5 and MY_LONG-5 <= longitude <= MY_LONG+5:
        return True

def is_night():
    parameters = {
        "lat": MY_LAT,
        "lng": MY_LONG,
        "formatted": 0,
    }
    response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
    response.raise_for_status()
    data = response.json()
    sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
    sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])
    lt_sunrise = utc_to_local(sunrise)
    lt_sunset = utc_to_local(sunset)

    time_now = datetime.now().hour

    if time_now >= lt_sunset or time_now <= lt_sunrise:
        return True
while True:
    time.sleep(1800)
    if is_isss_overhead() and is_night():
        connection = smtplib.SMTP(os.getenv("SMTP"), port=os.getenv("PORT"))
        connection.starttls()
        connection.login(MY_EMAIL, MY_PASSWORD)
        connection.sendmail(
            from_addr=MY_EMAIL,
            to_addrs=MY_EMAIL,
            msg="Subject:Look up!\n\nThe ISS is above you in the sky."
        )

