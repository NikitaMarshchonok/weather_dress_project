from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# API ключи
WEATHERBIT_API_KEY = 'c597a50e22d54780982bc0d47ae768c4'
OPENCAGE_API_KEY = '8a54749920984b4b938c399523a190d8'
UNSPLASH_ACCESS_KEY = '26cZWTN_kD4rCV3lgy17S3bwPpmzG_qiyv42CfACjKU'


# Функция для получения данных гардероба
def get_wardrobe_info(temperature, weather_desc, wind_speed):
    print(
        f"Temperature: {temperature}, Weather: {weather_desc}, Wind Speed: {wind_speed}")  # Добавляем отладочный вывод

    wardrobe_images = []

    # Летняя погода
    if temperature > 21:
        wardrobe_images.append('summer/summer_outfit.webp')
        print("Selected: summer/summer_outfit.webp")

    # Весенняя погода
    elif 12 <= temperature <= 20:
        wardrobe_images.append('spring/spring_outfit.webp')
        print("Selected: spring/spring_outfit.webp")

    # Осенняя погода
    elif 4 <= temperature <= 11:
        wardrobe_images.append('autumn/autumn_outfit.webp')
        print("Selected: autumn/autumn_outfit.webp")

    # Зимняя погода
    else:  # Температура ниже 4°C
        wardrobe_images.append('winter/winter_outfit.webp')
        print("Selected: winter/winter_outfit.webp")

    # Добавление аксессуаров в зависимости от погоды
    if 'rain' in weather_desc.lower():
        wardrobe_images.append('other/umbrella.webp')
        print("Added: other/umbrella.webp")

    if temperature > 21 and 'clear' in weather_desc.lower():
        wardrobe_images.append('other/sunglasses.webp')
        print("Added: other/sunglasses.webp")

    # Для холодной и ветреной погоды добавляем шапку и шарф, если температура ниже 12°C
    if temperature < 12 and 'windy' in weather_desc.lower():
        wardrobe_images.append('other/hat.webp')
        wardrobe_images.append('other/scarf.webp')
        print("Added: other/hat.webp and other/scarf.webp")

    return wardrobe_images


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    destination = request.form['destination']
    date = request.form['date']

    # Получение координат города
    geocode_url = f"https://api.opencagedata.com/geocode/v1/json?q={destination}&key={OPENCAGE_API_KEY}"
    geocode_response = requests.get(geocode_url)
    geocode_data = geocode_response.json()

    if 'results' not in geocode_data or len(geocode_data['results']) == 0:
        return jsonify({'error': 'Could not retrieve location data'})

    lat = geocode_data['results'][0]['geometry']['lat']
    lon = geocode_data['results'][0]['geometry']['lng']

    if not lat or not lon:
        return jsonify({'error': 'Location data is incomplete'})

    # Получение прогноза погоды на 7 дней
    weather_url = f"https://api.weatherbit.io/v2.0/forecast/daily?lat={lat}&lon={lon}&key={WEATHERBIT_API_KEY}&days=7"
    weather_response = requests.get(weather_url)
    weather_data = weather_response.json()

    if 'data' not in weather_data:
        return jsonify({'error': 'Failed to retrieve weather data'})

    # Обработка данных для выбранной даты
    forecast = []
    wardrobe_images = []
    for entry in weather_data['data']:
        entry_date = entry['datetime']
        if entry_date == date:
            wardrobe_images = get_wardrobe_info(entry['temp'], entry['weather']['description'], entry['wind_spd'])
            forecast.append({
                'date': entry_date,
                'temperature': entry['temp'],
                'pressure': entry['pres'],
                'humidity': entry['rh'],
                'wind_speed': entry['wind_spd'],
                'weather': entry['weather']['description'],
                'wardrobe_images': wardrobe_images,
            })

    if not forecast:
        return jsonify({'error': 'No weather data available for the selected date'})

    # Получение изображений от Unsplash
    unsplash_url = f"https://api.unsplash.com/search/photos?query={destination}&client_id={UNSPLASH_ACCESS_KEY}"
    unsplash_response = requests.get(unsplash_url)
    unsplash_data = unsplash_response.json()

    image_urls = [image['urls']['small'] for image in unsplash_data['results']]

    return jsonify({'weather': forecast, 'images': image_urls})


if __name__ == '__main__':
    app.run(debug=True)
