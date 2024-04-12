import requests


def get_data_from_api():
    response = requests.get('https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5')
    return response.json()


if __name__ == '__main__':
    print(get_data_from_api())
