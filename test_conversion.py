# test_conversion.py
"""
Prueba la conversi?n de formato del parser al analyzer
"""

def american_to_decimal(american):
    if not american:
        return None
    american = str(american).replace('+', '')
    american = int(american)
    if american > 0:
        return round(1 + (american / 100), 2)
    else:
        return round(1 + (100 / abs(american)), 2)

# Simular un partido del parser
partido_parser = {
    'local': 'Puebla',
    'cuota_local': '+270',
    'empate': 'Empate',
    'cuota_empate': '+255',
    'visitante': 'Tigres UANL',
    'cuota_visitante': '-103'
}

print("?? PARTIDO DEL PARSER:")
print(partido_parser)

print("\n?? CONVERTIDO A FORMATO ANALYZER:")
print(f"Local: {partido_parser['local']}")
print(f"Visitante: {partido_parser['visitante']}")
print(f"Cuota local (decimal): {american_to_decimal(partido_parser['cuota_local'])}")
print(f"Cuota empate (decimal): {american_to_decimal(partido_parser['cuota_empate'])}")
print(f"Cuota visitante (decimal): {american_to_decimal(partido_parser['cuota_visitante'])}")

# Crear el formato completo
odds_dict = {
    'home_odds': american_to_decimal(partido_parser['cuota_local']),
    'draw_odds': american_to_decimal(partido_parser['cuota_empate']),
    'away_odds': american_to_decimal(partido_parser['cuota_visitante']),
    'all_odds': [
        american_to_decimal(partido_parser['cuota_local']),
        american_to_decimal(partido_parser['cuota_empate']),
        american_to_decimal(partido_parser['cuota_visitante'])
    ]
}

print("\n?? ODDS DICT para analyzer:")
print(odds_dict)
