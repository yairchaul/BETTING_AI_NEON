# test_apis_reales.py
from modules.smart_searcher import SmartSearcher
import json

print(' PRUEBA DE CONEXIÓN CON APIS REALES')
print('=' * 60)

searcher = SmartSearcher()

print(f'\n API Keys configuradas:')
print(f'   Football API: {"" if searcher.football_api_key else ""}')
print(f'   Google API: {"" if searcher.google_api_key else ""}')
print(f'   Odds API: {"" if searcher.odds_api_key else ""}')
print(f'   Groq: {"" if searcher.groq_client else ""}')

# Probar búsqueda en Football-API
if searcher.football_api_key:
    print('\n Probando Football-API para Puebla...')
    try:
        import requests
        url = 'https://v3.football.api-sports.io/teams'
        params = {'search': 'Puebla', 'country': 'Mexico'}
        headers = {
            'x-rapidapi-key': searcher.football_api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }
        response = requests.get(url, headers=headers, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f'    Respuesta: {json.dumps(data, indent=2)[:500]}...')
        else:
            print(f'    Error {response.status_code}')
    except Exception as e:
        print(f'    Error: {e}')

# Probar Groq para análisis contextual
if searcher.groq_client:
    print('\n Probando Groq para análisis...')
    try:
        prompt = 'Analiza rápidamente el partido Puebla vs Tigres UANL. Da solo 3 factores clave.'
        response = searcher.groq_client.chat.completions.create(
            model='mixtral-8x7b-32768',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.3,
            max_tokens=100
        )
        print(f'    Respuesta: {response.choices[0].message.content}')
    except Exception as e:
        print(f'    Error: {e}')
