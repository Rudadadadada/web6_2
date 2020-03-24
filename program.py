import sys
from io import BytesIO
import requests
from PIL import Image
from get_delta import get_spn

dictionary = {'Зеленый': [], 'Синий': [], 'Серый': []}

toponym_to_find = " ".join(sys.argv[1:])

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": toponym_to_find,
    "format": "json"}

response = requests.get(geocoder_api_server, params=geocoder_params)

json_response = response.json()
toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
toponym_coodrinates_f = toponym["Point"]["pos"]
toponym_longitude, toponym_lattitude = toponym_coodrinates_f.split(" ")

delta = str(get_spn(toponym_to_find) + 0.01)

search_api_server = "https://search-maps.yandex.ru/v1/"
search_params = {
    "apikey": "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3",
    "text": "аптека",
    "lang": "ru_RU",
    "ll": ','.join(toponym_coodrinates_f.split()),
    "type": "biz"
}

response = requests.get(search_api_server, params=search_params)
if not response:
    print('Ошибка при запросе изображения!')
    exit(0)

json_response_farm = response.json()
for i in range(10):
    address = json_response_farm["features"][i]["properties"]["CompanyMetaData"]["address"]
    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": address,
        "format": "json"}
    response = requests.get(geocoder_api_server, params=geocoder_params)
    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    toponym_coodrinates = toponym["Point"]["pos"]
    try:
        hours = json_response_farm["features"][i]["properties"]["CompanyMetaData"]["Hours"]["text"]
        if 'круглосуточно' in hours:
            dictionary['Зеленый'].append(toponym_coodrinates.replace(' ', ','))
        else:
            dictionary['Синий'].append(toponym_coodrinates.replace(' ', ','))
    except Exception:
        dictionary['Серый'].append(toponym_coodrinates.replace(' ', ','))
map_params = {
    "ll": ",".join([toponym_longitude, toponym_lattitude]),
    "spn": ",".join([delta, delta]),
    "l": "map",
    "pt": f"{''.join([i + ',pmblm~' for i in dictionary['Синий']])}"
          f"{''.join([i + ',pmgnm~' for i in dictionary['Зеленый']])}"
          f"{''.join([i + ',pmgrm~' for i in dictionary['Серый']])}"
          f"{toponym_coodrinates_f.replace(' ', ',')},flag"
}

map_api_server = "http://static-maps.yandex.ru/1.x/"
response = requests.get(map_api_server, params=map_params)

Image.open(BytesIO(
    response.content)).show()