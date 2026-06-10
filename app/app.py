from flask import Flask, render_template, request
import requests
import redis
import json
import os

app = Flask(__name__)

# Redis connection
cache = redis.Redis(host='redis', port=6379, decode_responses=True)

API_KEY = 'bee332f3b88484e806b845fb72f9f15c'
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'
FORECAST_URL = 'http://api.openweathermap.org/data/2.5/forecast'

@app.route('/', methods=['GET', 'POST'])
def index():
    weather = None
    forecast = None
    error = None

    if request.method == 'POST':
        city = request.form.get('city')

        # Check Redis cache first
        cached = cache.get(city)
        if cached:
            weather = json.loads(cached)
        else:
            # Call API
            response = requests.get(BASE_URL, params={
                'q': city,
                'appid': API_KEY,
                'units': 'metric'
            })
            if response.status_code == 200:
                weather = response.json()
                # Save to cache for 10 minutes
                cache.setex(city, 600, json.dumps(weather))
            else:
                error = 'City not found!'

        # Forecast
        if weather:
            f_response = requests.get(FORECAST_URL, params={
                'q': city,
                'appid': API_KEY,
                'units': 'metric',
                'cnt': 5
            })
            if f_response.status_code == 200:
                forecast = f_response.json()['list']

    return render_template('index.html', weather=weather, forecast=forecast, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)