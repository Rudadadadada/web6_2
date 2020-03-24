import requests


def get_spn(address):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": address,
        "format": "json"}
    response = requests.get(geocoder_api_server, params=geocoder_params)
    if not response:
        print('Ошибка!')
        exit(0)
    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    toponym_upper_corner = list(map(float, toponym['boundedBy']['Envelope']['upperCorner'].split()))
    toponym_lower_corner = list(map(float, toponym['boundedBy']['Envelope']['lowerCorner'].split()))
    delta = abs(toponym_lower_corner[0] - toponym_upper_corner[0])
    return delta
