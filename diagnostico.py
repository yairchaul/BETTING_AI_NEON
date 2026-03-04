import streamlit as st
import os
import tomllib

print("🔬 DIAGNÓSTICO COMPLETO")
print("=" * 50)

# 1. Verificar ubicación actual
print(f"📁 Directorio actual: {os.getcwd()}")

# 2. Verificar si existe el archivo
secrets_path = os.path.join('.streamlit', 'secrets.toml')
if os.path.exists(secrets_path):
    print(f"✅ Archivo existe: {secrets_path}")
    print(f"📏 Tamaño: {os.path.getsize(secrets_path)} bytes")
else:
    print(f"❌ No existe: {secrets_path}")

# 3. Leer el archivo directamente
try:
    with open(secrets_path, 'rb') as f:
        data = tomllib.load(f)
        print("\n📋 CONTENIDO DEL ARCHIVO (lectura directa):")
        for key in data:
            if key == 'ODDS_API_KEY':
                print(f"   ✅ {key}: {data[key][:5]}...")
            else:
                print(f"   📌 {key}: {type(data[key]).__name__}")
except Exception as e:
    print(f"❌ Error leyendo archivo: {e}")

# 4. Ver qué ve Streamlit
try:
    print("\n📋 LO QUE VE STREAMLIT:")
    all_secrets = st.secrets
    for key in all_secrets:
        if key == 'ODDS_API_KEY':
            print(f"   ✅ {key}: {all_secrets[key][:5]}...")
        else:
            print(f"   📌 {key}: {type(all_secrets[key]).__name__}")
except Exception as e:
    print(f"❌ Error con st.secrets: {e}")

print("=" * 50)
