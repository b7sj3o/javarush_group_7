import requests


api_key = 'ВАШ_КЛЮЧ_OPENWEATHERMAP'

def parse_data(city: str):
    """
    :param city:
    :return:
    """
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url=url)
    # Парсимо відповідь!
    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['description']
        temperature = data['main']['temp']
        print(f"У місті {city} зараз {temperature}°C")
    elif response.status_code == 429:
        print("Забагато запитів, спробуйте пізніше")
    elif response.status_code == 404:
        print("Такого міста не знайдено")
    else:
        print("Помилка!!! при отриманні даних про погоду.")


while False:
    city = input(">>> ")
    if not city:
        continue

    parse_data(city)