import requests

API_KEY = '05b9723d89e43cf50594304fe3ee0f8e'
headers = {
    'x-apisports-key': API_KEY
}

print(' VERIFICANDO CONEXIÓN A API-FOOTBALL')
print('=' * 60)

# Verificar estado
url = "https://v3.football.api-sports.io/status"
response = requests.get(url, headers=headers)
print(f' Status: {response.status_code}')
data = response.json()
print(f' Respuesta: {data}')

if 'errors' in data and data['errors']:
    print(f' ERROR: {data["errors"]}')
else:
    print(' CONEXIÓN EXITOSA!')
    print(f'   Cuenta: {data["response"]["account"]["email"]}')
    print(f'   Plan: {data["response"]["subscription"]["plan"]}')
    print(f'   Requests hoy: {data["response"]["requests"]["current"]}/{data["response"]["requests"]["limit_day"]}')
