import requests
import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup


TOKEN = '8739271002:AAGik7n_a2cJN4M1jrHa3x2IszTdZjKTB4c'
bot = telebot.TeleBot(TOKEN)

URL = 'https://api.openweathermap.org/data/2.5/weather'
WEATHER_TOKEN = '7eddfa02d96c7a26d7c4a7b13848c023'

def get_emoji(value, thresholds):
    for limit, emoji in thresholds:
        if value < limit:
            return emoji
    return thresholds[-1][1]

TEMP_EMOJI = [(0, '🥶'), (10, '🧥'), (20, '🌤️'), (30, '😎'), (999, '🥵')]
FEELS_EMOJI = [(0, '🥶'), (10, '🧣'), (20, '🙂'), (30, '😎'), (999, '🥵')]
HUMIDITY_EMOJI = [(30, '🏜️'), (60, '💧'), (999, '🌊')]

WEATHER_EMOJI = {
    range(200,300):'⛈️', range(300,400):'🌦️', range(500,600):'🌧️',
    range(600,700):'❄️', range(700,800):'🌫️', range(800,801):'☀️',
}

def get_weather(lat, lon):
    try:
        params = {'lat': lat,
                'lon': lon,
                'units': 'metric',
                'lang': 'ru',
                'appid': WEATHER_TOKEN}
        data = requests.get(url=URL, params=params, timeout=5).json()
    except requests.exceptions.Timeout:
        return '⏱️ Сервер погоды не отвечает, попробуй позже'
    except Exception:
        return '❌ Ошибка при получении погоды'

    if 'weather' not in data:
        return f'❌ Ошибка API: {data.get("message", "неизвестная ошибка")}'

    desc = data['weather'][0]['description']
    temp = data['main']['temp']
    feels_like = data['main']['feels_like']
    city = data['name']
    humidity = data['main']['humidity']
    weather_id = data['weather'][0]['id']

    w_emoji = next((e for r,e in WEATHER_EMOJI.items() if weather_id in r), '☁️')

    text = (f'🏙️ Погода в: {city}\n'
            f'{w_emoji} {desc}\n'
            f'{get_emoji(temp, TEMP_EMOJI)} Температура: {temp}°C\n'
            f'{get_emoji(feels_like, FEELS_EMOJI)} Ощущается как: {feels_like}°C\n'
            f'{get_emoji(humidity, HUMIDITY_EMOJI)} Влажность: {humidity}%')

    return text

def get_weather_by_city(city_name):
    try:
        params = {
            'q': city_name,
            'units': 'metric',
            'lang': 'ru',
            'appid': WEATHER_TOKEN}
        data = requests.get(URL, params=params, timeout=5).json()
    except requests.exceptions.Timeout:
        return '⏱️ Сервер погоды не отвечает, попробуй позже'
    except Exception:
        return '❌ Ошибка при получении погоды'

    if 'weather' not in data:  # ← добавь эту проверку
        return f'❌ Ошибка API: {data.get("message", "неизвестная ошибка")}'

    if data.get('cod') != 200:  # city not found
        return None

    desc       = data['weather'][0]['description']
    temp       = data['main']['temp']
    feels_like = data['main']['feels_like']
    city       = data['name']
    humidity   = data['main']['humidity']
    weather_id = data['weather'][0]['id']

    w_emoji = next((e for r,e in WEATHER_EMOJI.items() if weather_id in r), '☁️')

    return (f'🏙️ Погода в {city}:\n'
            f'{w_emoji} {desc}\n'
            f'{get_emoji(temp, TEMP_EMOJI)} Температура: {temp}°C\n'
            f'{get_emoji(feels_like, FEELS_EMOJI)} Ощущается как: {feels_like}°C\n'
            f'{get_emoji(humidity, HUMIDITY_EMOJI)} Влажность: {humidity}%')



keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton('Получить погоду', request_location=True))
keyboard.add(KeyboardButton('О проэкте'))

@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = 'Отправь свое местоположения и я отправлю тебе погоду'
    bot.send_message(message.chat.id, text, reply_markup=keyboard)

@bot.message_handler(commands=['about'])
@bot.message_handler(func=lambda m: m.text == 'О проэкте')
def send_about(message):
    text = 'уыуыуы'
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: len(m.text.split()) == 2 and all(
    p.replace('.','').replace('-','').isdigit() for p in m.text.split()
))
def send_weather_by_text(message):
    lat, lon = map(float, message.text.split())
    result = get_weather(lat, lon)
    if result:
        bot.send_message(message.chat.id, result, reply_markup=keyboard)

@bot.message_handler(func=lambda m: True)  # catches all remaining text
def send_weather_by_city(message):
    result = get_weather_by_city(message.text)
    if result:
        bot.send_message(message.chat.id, result, reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, f'❌ Город "{message.text}" не найден', reply_markup=keyboard)

@bot.message_handler(content_types=['location'])
def send_weather(message):
    lat = message.location.latitude
    lon = message.location.longitude
    result = get_weather(lat, lon)
    if result:
        bot.send_message(message.chat.id, result, reply_markup=keyboard)

bot.infinity_polling()

