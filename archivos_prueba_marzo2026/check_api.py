import requests
import streamlit as st

print("🔍 VERIFICANDO API KEY")
print("=" * 60)

# Cargar API key desde secrets
try:
    api_key = st.secrets.get("FOOTBALL_API_KEY", "")
    print(f"API Key encontrada: {api_key[:5]}...{api_key[-5:]}")
except Exception as e:
    print(f"Error cargando secrets: {e}")
    api_key = ""

headers = {'x-apisports-key': api_key}

# Probar status
url = "https://v3.football.api-sports.io/status"
try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('response'):
            account = data['response'].get('account', {})
            print(f"Cuenta: {account.get('email', 'N/A')}")
            print(f"Plan: {data['response'].get('subscription', {}).get('plan', 'N/A')}")
        else:
            print("Error en respuesta:", data)
    else:
        print(f"Error: {response.status_code}")
        print(response.text[:200])
except Exception as e:
    print(f"Error de conexión: {e}")

print("=" * 60)
