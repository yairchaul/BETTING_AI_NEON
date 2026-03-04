# test_cobertura_ligas.py
from modules.odds_api_integrator import OddsAPIIntegrator

print("?? VERIFICANDO COBERTURA DE LIGAS")
print("=" * 80)

odds_api = OddsAPIIntegrator()

# Obtener todos los deportes disponibles
sports = odds_api.get_sports()

print(f"\n?? TOTAL DE LIGAS/DEPORTES EN API: {len(sports)}")
print("-" * 80)

# Palabras clave para buscar ligas de inter?s
keywords = {
    "M?xico": ["mex", "liga mx", "mexico", "mexican"],
    "Brasil": ["brazil", "brasil", "serie a", "carioca", "paulista", "mineiro", "gaucho"],
    "Argentina": ["argentina", "arg", "primera", "superliga", "copa"],
    "Chile": ["chile", "primera"],
    "Colombia": ["colombia", "primera a", "liga colombiana"],
    "Per?": ["peru", "liga 1"],
    "Uruguay": ["uruguay", "primera"],
    "Paraguay": ["paraguay", "primera"],
    "Ecuador": ["ecuador", "serie a"],
    "EE.UU.": ["usa", "mls", "united states"],
    "Costa Rica": ["costa rica", "primera"],
    "Guatemala": ["guatemala", "liga nacional"],
    "Panam?": ["panama", "liga panamena"],
    "Jamaica": ["jamaica", "premier league"],
    "Nicaragua": ["nicaragua", "primera"],
    "Internacional": ["libertadores", "sudamericana", "concacaf", "conmebol", "uefa"],
}

encontradas = {}

for sport in sports:
    title = sport.get('title', '').lower()
    key = sport.get('key', '').lower()
    description = sport.get('description', '').lower()
    grupo = sport.get('group', '').lower()
    
    texto_completo = f"{title} {key} {description} {grupo}"
    
    for pais, palabras in keywords.items():
        for palabra in palabras:
            if palabra in texto_completo:
                if pais not in encontradas:
                    encontradas[pais] = []
                encontradas[pais].append(sport)
                break

# Mostrar resultados
for pais, ligas in encontradas.items():
    print(f"\n{pais}: {len(ligas)} ligas encontradas")
    for liga in ligas[:5]:  # Mostrar primeras 5
        print(f"   ? {liga.get('title')} ({liga.get('key')})")
    if len(ligas) > 5:
        print(f"   ... y {len(ligas)-5} m?s")

print("\n" + "=" * 80)
