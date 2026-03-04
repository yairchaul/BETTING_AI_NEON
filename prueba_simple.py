import streamlit as st

print("🔬 PRUEBA ULTRA SIMPLE")
print("=" * 40)

try:
    # Intentar acceder directamente a la key
    key = st.secrets["ODDS_API_KEY"]
    print(f"✅ ¡ÉXITO! Key encontrada: {key[:5]}...{key[-5:]}")
    
    # Mostrar todas las keys disponibles
    print("\n📋 Keys disponibles en secrets:")
    for k in st.secrets.keys():
        if k != "ODDS_API_KEY":
            print(f"   - {k}")
            
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n🔍 Diagnóstico:")
    print("1. Verifica que el archivo existe: .streamlit/secrets.toml")
    print("2. Verifica el contenido:")
    try:
        with open(".streamlit/secrets.toml", "r") as f:
            content = f.read()
            print(f"\nContenido del archivo:\n{content[:200]}...")
    except:
        print("No se pudo leer el archivo")
