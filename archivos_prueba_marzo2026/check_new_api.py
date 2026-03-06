import requests
import streamlit as st

print("🔍 VERIFICANDO NUEVA API KEY")
print("=" * 60)

api_key = st.secrets.get("FOOTBALL_API_KEY", "")
print(f"API Key: {api_key[:5]}...{api_key[-5:]}")

headers = {'x-apisports-key': api_key}
base_url = "https://v3.football.api-sports.io"

# Probar endpoint de países
try:
    response = requests.get(f"{base_url}/countries", headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        paises = data.get('response', [])
        print(f"✅ Países encontrados: {len(paises)}")
        if paises:
            print("Primeros 5 países:")
            for p in paises[:5]:
                print(f"  - {p.get('name', 'N/A')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text[:200])
except Exception as e:
    print(f"Error: {e}")

print("=" * 60)
