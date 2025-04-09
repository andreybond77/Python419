import json
import os
from datetime import datetime
from dotenv import load_dotenv
import requests
from requests import exceptions


class WeatherAPI:
    def __init__(self, api_key):
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.api_key = api_key

    def get_weather(self, city):
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric',
            'lang': 'ru'
        }
        try:
            response = requests.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            return {
                'city': city,
                'temp': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'timestamp': datetime.now().isoformat()  # Добавляем временную метку
            }
        except exceptions.HTTPError as ex:
            if response.status_code == 404:
                print(f'Город {city} не найден.')
            else:
                print(f'Ошибка API: {ex}')
        except exceptions.Timeout:
            print('Сервер не ответил за 5 секунд')
        except exceptions.RequestException as ex:
            print(f'Ошибка подключения: {ex}')
        return None

    @classmethod
    def save_to_json(cls, data, filename='weather_history.json'):
        # Проверяем, существует ли файл
        if os.path.exists(filename):
            try:
                # Если файл существует, загружаем существующие данные
                with open(filename, 'r', encoding='utf-8') as fp:
                    existing_data = json.load(fp)
            except (json.JSONDecodeError, FileNotFoundError):
                # Если файл поврежден или не найден, начинаем новую историю
                existing_data = []
        else:
            existing_data = []

        # Добавляем новые данные к существующим
        existing_data.append(data)

        # Сохраняем обновленные данные в файл
        with open(filename, 'w', encoding='utf-8') as fp:
            json.dump(existing_data, fp, ensure_ascii=False, indent=4)
        print(f'Данные сохранены в {filename}')


if __name__ == "__main__":
    load_dotenv()
    API_KEY = os.getenv('API_KEY')
    if API_KEY is None:
        print("API_KEY не найден. Пожалуйста, проверьте файл .env.")
        exit(1)

    weather_app = WeatherAPI(API_KEY)
    city = input("Введите город: ")
    weather_data = weather_app.get_weather(city)

    if weather_data:
        print(f"\nПогода в {city}:")
        print(f"Температура: {weather_data['temp']}°C")
        print(f"Ощущается как: {weather_data['feels_like']}°C")
        print(f"Влажность: {weather_data['humidity']}%")
        print(f"Описание: {weather_data['description']}")

        WeatherAPI.save_to_json(weather_data)
    else:
        print("Не удалось получить данные о погоде.")
