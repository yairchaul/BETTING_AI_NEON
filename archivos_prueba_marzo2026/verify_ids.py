import requests

API_KEY = '05b9723d89e43cf50594304fe3ee0f8e'
headers = {'x-apisports-key': API_KEY}

print("🔍 VERIFICANDO IDs DE LIGAS MEXICANAS")
print("=" * 60)

url = "https://v3.football.api-sports.io/leagues"
params = {"country": "Mexico"}

response = requests.get(url, headers=headers, params=params)
data = response.json()

print(f"\n📊 LIGAS ENCONTRADAS: {len(data['response'])}")
for league in data['response']:
    league_id = league['league']['id']
    league_name = league['league']['name']
    print(f"ID: {league_id} - {league_name}")
    
    if 'femenil' in league_name.lower() or 'women' in league_name.lower():
        print(f"  ✅ LIGA FEMENIL DETECTADA: {league_name} (ID: {league_id})")

print("\n" + "=" * 60)
