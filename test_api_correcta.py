# test_api_correcta.py
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_KEY = "98ccdb7d4c28042caa8bc8fe7ff6cc62"

print("?? PROBANDO DIFERENTES URLS Y PAR?METROS")
print("=" * 60)

# Lista de posibles combinaciones
tests = [
    {"url": "https://api.oddsapi.io/v1/sports", "params": {"apiKey": API_KEY}},
    {"url": "https://api.oddsapi.io/v2/sports", "params": {"apiKey": API_KEY}},
    {"url": "https://api.oddsapi.io/v3/sports", "params": {"apiKey": API_KEY}},
    {"url": "https://api.odds-api.io/v1/sports", "params": {"apiKey": API_KEY}},
    {"url": "https://api.odds-api.io/v2/sports", "params": {"apiKey": API_KEY}},
    {"url": "https://api.odds-api.io/v3/sports", "params": {"apiKey": API_KEY}},
    {"url": "https://odds-api.io/api/v1/sports", "params": {"apiKey": API_KEY}},
    {"url": "https://api.theoddsapi.com/v4/sports", "params": {"apiKey": API_KEY}},  # Otra API popular
]

for i, test in enumerate(tests, 1):
    print(f"\n{i}. Probando: {test['url']}")
    try:
        response = requests.get(test['url'], params=test['params'], verify=False, timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ? ??XITO!")
            print(f"   Respuesta: {response.text[:200]}...")
            break
        elif response.status_code == 401:
            print(f"   ? Error 401 - API Key inv?lida o formato incorrecto")
        else:
            print(f"   ? Error {response.status_code}")
    except Exception as e:
        print(f"   ? Error de conexi?n: {e}")

print("\n" + "=" * 60)
