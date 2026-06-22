from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

# Support running as a PyInstaller .exe (launcher.py sets WEAZZAR_BASE_DIR)
base_dir = os.environ.get('WEAZZAR_BASE_DIR') or os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, '.env'))

app = Flask(__name__,
            static_folder=os.path.join(base_dir, 'static'),
            template_folder=os.path.join(base_dir, 'templates'))

WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', '')
GEOAPIFY_API_KEY = os.environ.get('GEOAPIFY_API_KEY', '')


@app.after_request
def set_response_headers(response):
    if response.content_type and 'text/html' in response.content_type:
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response


def get_condition_emoji(condition_text):
    c = condition_text.lower()
    if any(w in c for w in ['thunder', 'storm']):        return '⛈️'
    if any(w in c for w in ['blizzard', 'blowing snow']): return '🌨️'
    if any(w in c for w in ['snow', 'sleet', 'ice']):    return '❄️'
    if any(w in c for w in ['heavy rain', 'torrential']): return '🌧️'
    if any(w in c for w in ['rain', 'drizzle', 'shower']): return '🌦️'
    if any(w in c for w in ['fog', 'mist', 'haze']):     return '🌫️'
    if 'overcast' in c:                                   return '☁️'
    if 'cloud' in c:                                      return '⛅'
    if any(w in c for w in ['clear', 'sunny']):           return '☀️'
    return '🌤️'


def get_weather_theme(condition_text, is_day, temp_c):
    c = condition_text.lower()
    if any(w in c for w in ['thunder', 'storm']):         return 'storm'
    if any(w in c for w in ['snow', 'blizzard', 'sleet', 'ice']): return 'snow'
    if any(w in c for w in ['fog', 'mist', 'haze']):     return 'fog'
    if any(w in c for w in ['rain', 'drizzle', 'shower']): return 'rain'
    if any(w in c for w in ['cloud', 'overcast']):        return 'cloudy'
    if not is_day:                                         return 'night'
    if temp_c >= 35:                                       return 'hot'
    return 'sunny'


def process_weather_data(city_name):
    try:
        url = (
            f'https://api.weatherapi.com/v1/forecast.json'
            f'?key={WEATHER_API_KEY}&q={city_name}&days=7&aqi=no&alerts=no'
        )
        response = requests.get(url, timeout=10)
        data = response.json()

        if 'error' in data:
            return {'error': data['error'].get('message',
                    'City not found. Please check the spelling and try again.')}

        cur = data['current']
        loc = data['location']

        temp_c       = cur['temp_c']
        fl_c         = cur['feelslike_c']
        condition    = cur['condition']['text']
        uv           = cur['uv']
        pressure_mb  = cur['pressure_mb']
        wind_kph     = cur['wind_kph']
        wind_dir     = cur['wind_dir']
        humidity_pct = cur['humidity']
        vis_km       = cur['vis_km']
        is_day       = bool(cur['is_day'])

        latitude      = loc['lat']
        longitude     = loc['lon']
        location_name = f"{loc['name']}, {loc['region']}, {loc['country']}"

        map_url = (
            f"https://maps.geoapify.com/v1/staticmap?style=osm-bright-smooth"
            f"&width=600&height=400&center=lonlat%3A{longitude}%2C{latitude}"
            f"&zoom=13&marker=lonlat%3A{longitude}%2C{latitude}"
            f"%3Btype%3Aawesome%3Bcolor%3A%23667eea%3Bsize%3Ax-large%3Bicon%3Acloud"
            f"&apiKey={GEOAPIFY_API_KEY}"
        )

        # Temperature (both units)
        temp_num   = int(round(temp_c))
        temp_num_f = int(round(temp_c * 9 / 5 + 32))

        if temp_c < 0:      temp_label = 'Freezing'
        elif temp_c < 10:   temp_label = 'Cold'
        elif temp_c < 20:   temp_label = 'Cool'
        elif temp_c < 30:   temp_label = 'Warm'
        else:               temp_label = 'Hot'
        temperature = f"{temp_c:.1f}°C · {temp_label}"

        # Feels like (both units)
        feelslike_c = round(fl_c, 1)
        feelslike_f = round(fl_c * 9 / 5 + 32, 1)

        # UV
        if uv < 3:    uv_rays = f"{uv} — Low";       uv_class = 'val-good'
        elif uv < 6:  uv_rays = f"{uv} — Moderate";  uv_class = 'val-neutral'
        elif uv < 8:  uv_rays = f"{uv} — High";      uv_class = 'val-warn'
        elif uv < 11: uv_rays = f"{uv} — Very High"; uv_class = 'val-bad'
        else:         uv_rays = f"{uv} — Extreme";   uv_class = 'val-bad'
        uv_pct = min(int(uv / 11 * 100), 100)

        # Pressure
        if pressure_mb < 1000:   pressure = f"{pressure_mb} mb · Low";    pressure_class = 'val-warn'
        elif pressure_mb < 1020: pressure = f"{pressure_mb} mb · Normal"; pressure_class = 'val-good'
        else:                    pressure = f"{pressure_mb} mb · High";   pressure_class = 'val-neutral'
        pressure_pct = min(int((pressure_mb - 960) / (1040 - 960) * 100), 100)

        # Wind (speed + direction)
        if wind_kph < 20:   wind_label = 'Calm';       wind_class = 'val-good'
        elif wind_kph < 40: wind_label = 'Breezy';     wind_class = 'val-neutral'
        elif wind_kph < 60: wind_label = 'Windy';      wind_class = 'val-warn'
        else:               wind_label = 'Very Windy'; wind_class = 'val-bad'
        wind_speed = f"{wind_kph} kph {wind_dir} · {wind_label}"
        wind_pct   = min(int(wind_kph / 80 * 100), 100)

        # Humidity
        if humidity_pct < 30:   humidity = f"{humidity_pct}% · Low";      humidity_class = 'val-neutral'
        elif humidity_pct < 60: humidity = f"{humidity_pct}% · Moderate"; humidity_class = 'val-good'
        elif humidity_pct < 80: humidity = f"{humidity_pct}% · High";     humidity_class = 'val-warn'
        else:                   humidity = f"{humidity_pct}% · Very High"; humidity_class = 'val-bad'

        # Visibility
        if vis_km < 1:    visibility = f"{vis_km} km · Very Poor"; vis_class = 'val-bad'
        elif vis_km < 5:  visibility = f"{vis_km} km · Poor";      vis_class = 'val-warn'
        elif vis_km < 10: visibility = f"{vis_km} km · Moderate";  vis_class = 'val-neutral'
        else:             visibility = f"{vis_km} km · Clear";     vis_class = 'val-good'
        vis_pct = min(int(vis_km / 20 * 100), 100)

        # Feels like color
        diff = fl_c - temp_c
        if abs(diff) < 2:   feels_class = 'val-good'
        elif abs(diff) < 5: feels_class = 'val-neutral'
        else:               feels_class = 'val-warn'

        # 7-Day Forecast
        forecast_days = []
        for i, day in enumerate(data['forecast']['forecastday']):
            date_obj = datetime.strptime(day['date'], '%Y-%m-%d')
            d = day['day']
            forecast_days.append({
                'day':       'Today' if i == 0 else date_obj.strftime('%a'),
                'emoji':     get_condition_emoji(d['condition']['text']),
                'condition': d['condition']['text'],
                'max_c':     int(round(d['maxtemp_c'])),
                'min_c':     int(round(d['mintemp_c'])),
                'max_f':     int(round(d['maxtemp_c'] * 9 / 5 + 32)),
                'min_f':     int(round(d['mintemp_c'] * 9 / 5 + 32)),
                'rain':      d['daily_chance_of_rain'],
            })

        # Today high/low
        today_max_c = forecast_days[0]['max_c'] if forecast_days else temp_num
        today_min_c = forecast_days[0]['min_c'] if forecast_days else temp_num
        today_max_f = forecast_days[0]['max_f'] if forecast_days else temp_num_f
        today_min_f = forecast_days[0]['min_f'] if forecast_days else temp_num_f

        # SVG sparkline (7-day max temps)
        max_temps = [d['max_c'] for d in forecast_days]
        if len(max_temps) > 1:
            mn, mx = min(max_temps) - 2, max(max_temps) + 2
            sw, sh = 560, 48
            pts = ' '.join(
                f"{(i/(len(max_temps)-1))*sw:.1f},{sh - ((t-mn)/(mx-mn))*sh:.1f}"
                for i, t in enumerate(max_temps)
            )
            circles = ''.join(
                f'<circle cx="{(i/(len(max_temps)-1))*sw:.1f}" cy="{sh - ((t-mn)/(mx-mn))*sh:.1f}" r="3.5" fill="rgba(255,255,255,0.9)"/>'
                for i, t in enumerate(max_temps)
            )
            sparkline = (
                f'<svg viewBox="0 0 {sw} {sh}" preserveAspectRatio="none" class="temp-sparkline">'
                f'<defs><linearGradient id="sg" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0%" stop-color="rgba(255,255,255,0.15)"/>'
                f'<stop offset="100%" stop-color="rgba(255,255,255,0)"/>'
                f'</linearGradient></defs>'
                f'<polyline points="{pts}" fill="none" stroke="rgba(255,255,255,0.55)" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>'
                f'{circles}'
                f'</svg>'
            )
        else:
            sparkline = ''

        # Display date
        _now = datetime.now()
        display_date = _now.strftime('%A, %B ') + str(_now.day)

        condition_emoji = get_condition_emoji(condition)
        theme           = get_weather_theme(condition, is_day, temp_c)

        return {
            'city':            city_name,
            'location':        location_name,
            'map_url':         map_url,
            'temp_num':        temp_num,
            'temp_num_f':      temp_num_f,
            'temperature':     temperature,
            'feelslike_c':     feelslike_c,
            'feelslike_f':     feelslike_f,
            'feels_class':     feels_class,
            'condition':       condition,
            'condition_emoji': condition_emoji,
            'theme':           theme,
            'uv_rays':         uv_rays,
            'uv_class':        uv_class,
            'uv_pct':          uv_pct,
            'pressure':        pressure,
            'pressure_class':  pressure_class,
            'pressure_pct':    pressure_pct,
            'wind_speed':      wind_speed,
            'wind_class':      wind_class,
            'wind_pct':        wind_pct,
            'humidity':        humidity,
            'humidity_class':  humidity_class,
            'humidity_pct':    humidity_pct,
            'visibility':      visibility,
            'vis_class':       vis_class,
            'vis_pct':         vis_pct,
            'today_max_c':     today_max_c,
            'today_min_c':     today_min_c,
            'today_max_f':     today_max_f,
            'today_min_f':     today_min_f,
            'sparkline':       sparkline,
            'display_date':    display_date,
            'forecast':        forecast_days,
            'error':           None
        }
    except requests.exceptions.Timeout:
        return {'error': 'Request timed out. Please try again.'}
    except Exception as e:
        app.logger.error(f'Weather fetch error: {type(e).__name__}: {e}')
        return {'error': 'Unable to fetch weather data. Please try again.'}


# ── PWA assets served with correct headers ──────────────────────────────────

@app.route('/sw.js')
def service_worker():
    resp = send_from_directory(os.path.join(base_dir, 'static'), 'sw.js')
    resp.headers['Content-Type'] = 'application/javascript'
    resp.headers['Service-Worker-Allowed'] = '/'
    resp.headers['Cache-Control'] = 'no-cache'
    return resp


@app.route('/manifest.json')
def manifest():
    return send_from_directory(os.path.join(base_dir, 'static'), 'manifest.json')


# ── Pages ────────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    return render_template('index.html', error=None)


@app.route('/privacy')
def privacy():
    return render_template('privacy.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


# ── API endpoints ────────────────────────────────────────────────────────────

@app.route('/api/search')
def api_search():
    query = request.args.get('q', '').strip()
    if len(query) < 2 or len(query) > 100:
        return jsonify([])
    try:
        url = f'https://api.weatherapi.com/v1/search.json?key={WEATHER_API_KEY}&q={query}'
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if isinstance(data, list):
            return jsonify([{
                'name':    item['name'],
                'region':  item['region'],
                'country': item['country']
            } for item in data[:6]])
        return jsonify([])
    except Exception as e:
        app.logger.error(f'Search error: {e}')
        return jsonify([])


@app.route('/api/weather/coords/<lat>/<lon>')
def api_weather_coords(lat, lon):
    try:
        url = f'https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={lat},{lon}'
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if 'error' in data:
            return jsonify({'error': data['error'].get('message', 'Location not found.')})
        return jsonify(process_weather_data(data['location']['name']))
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timed out. Please try again.'})
    except Exception:
        return jsonify({'error': 'Unable to fetch weather data. Please try again.'})


@app.route('/api/weather/<city>')
def api_weather(city):
    city = city.strip()
    if not city or len(city) > 100:
        return jsonify({'error': 'Invalid city name.'})
    return jsonify(process_weather_data(city))


@app.route('/weather', methods=['POST'])
def weather():
    city = request.form.get('city', '').strip()
    if not city:
        return render_template('index.html', error='Please enter a city name.')
    if len(city) > 100:
        return render_template('index.html', error='City name is too long.')
    weather_data = process_weather_data(city)
    if weather_data.get('error'):
        return render_template('index.html', error=weather_data['error'])
    return render_template('weather.html', **weather_data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
