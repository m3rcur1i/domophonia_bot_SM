from requests import *
import json

def check_tenant(phone):
    url = "https://domo-dev.profintel.ru/tg-bot/check-tenant"
    payload = "{\r\n    \"phone\": "+phone+"\r\n}"
    headers = {
    'X-API-KEY': 'SecretToken'
    }
    response = request("POST", url, headers=headers, data=payload)
    return response

def domo_apartment(tenant_id):
    url = f"https://domo-dev.profintel.ru/tg-bot/domo.apartment?tenant_id={tenant_id}"
    headers = {
    'X-API-KEY': 'SecretToken'
    }
    response = request("GET", url, headers=headers)

    data = [i for i in response.text.split('}}]},{')]
    data = [[b for b in i.split(",")] for i in data]
    apartments = [[i[0][i[0].find(":")+1:], i[1][8:-1], i[4][20:-1]] for i in data]

    return apartments

def get_photo(intercoms_id, tenant_id):
    url = f"https://domo-dev.profintel.ru/tg-bot/domo.domofon/urlsOnType?tenant_id={tenant_id}"
    payload = json.dumps({

        "intercoms_id": [
            intercoms_id
        ],
        "media_type": [
            "JPEG"
        ]
    })
    headers = {
        'x-api-key': 'SecretToken',
        'Content-Type': 'application/json'
    }

    response = request("POST", url, headers=headers, data=payload)
    data = [i for i in response.text.split(',')]
    return [data[1][8:-1], response.status_code]

def get_domophons(tenant_id, apartment_id):
    url = f"https://domo-dev.profintel.ru/tg-bot/domo.apartment/{apartment_id}/domofon?tenant_id={tenant_id}"
    headers = {
        'x-api-key': 'SecretToken'
    }
    response = request("GET", url, headers=headers)
    data = [i for i in response.text.split(',')]
    print(data)
    available_domophones = [[data[0][7:], data[1][8:-1]]] + [[data[i][6:], data[i+1][8:-1]] for i in range(1, len(data)) if i % 40 == 0]
    return available_domophones

def open_domophon(tenant_id, door_id):
    url = f"https://domo-dev.profintel.ru/tg-bot/domo.domofon/20/open?tenant_id={tenant_id}"
    payload = json.dumps({
      "door_id": door_id
    })
    headers = {
      'x-api-key': 'SecretToken'
    }
    response = request("POST", url, headers=headers, data=payload)

    return response.status_code

def webhook():
    url = "https://domophonia.app.n8n.cloud/webhook-test/?tenant_id:"

    payload = json.dumps({
        "intercoms_id": 20
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = request("POST", url, headers=headers, data=payload)

    print(response.text)

webhook()
# print(domo_apartment(22087))
# print(get_photo(20, 22087 ))
# print(get_domophons(22087, 3266))
