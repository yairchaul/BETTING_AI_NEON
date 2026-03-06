import requests
import streamlit as st

print("🔍 VERIFICANDO API KEY CON ENDPOINTS CORRECTOS")
print("=" * 60)

# Cargar API key
api_key = st.secrets.get("FOOTBALL_API_KEY", "")
print(f"API Key: {api_key[:5]}...{api_key[-5:]}")

headers = {'x-apisports-key': api_key}
base_url = "https://v3.football.api-sports.io"

# 1. PROBAR ENDPOINT DE PAÍSES (más básico)
print("\n📡 1. Probando endpoint de países...")
try:
    response = requests.get(f"{base_url}/countries", headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        paises = data.get('response', [])
        print(f"✅ Países encontrados: {len(paises)}")
    else:
        print(f"❌ Error: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# 2. PROBAR ENDPOINT DE LIGAS
print("\n📡 2. Probando endpoint de ligas...")
try:
    response = requests.get(f"{base_url}/leagues", headers=headers, params={"country": "Mexico"})
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        ligas = data.get('response', [])
        print(f"✅ Ligas mexicanas: {len(ligas)}")
        for liga in ligas:
            print(f"  - {liga['league']['name']}")
    else:
        print(f"❌ Error: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# 3. PROBAR ENDPOINT DE EQUIPOS
print("\n📡 3. Probando búsqueda de equipos...")
try:
    response = requests.get(f"{base_url}/teams", headers=headers, params={"search": "Puebla"})
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        equipos = data.get('response', [])
        print(f"✅ Equipos encontrados: {len(equipos)}")
        for equipo in equipos:
            team = equipo['team']
            print(f"  - {team['name']}")
    else:
        print(f"❌ Error: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
