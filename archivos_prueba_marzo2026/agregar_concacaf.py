#!/usr/bin/env python3
"""
Agregar equipos de la CONCACAF Champions Cup
"""
import json
import os

print("🌎 AGREGANDO CONCACAF CHAMPIONS CUP")
print("=" * 70)

# ============================================
# MÉXICO - Liga MX (equipos que participan en Concacaf)
# ============================================
equipos_mexico = [
    {"id": 2278, "name": "América", "country": "Mexico"},
    {"id": 2279, "name": "Guadalajara", "country": "Mexico"},
    {"id": 2280, "name": "Cruz Azul", "country": "Mexico"},
    {"id": 2281, "name": "Pumas UNAM", "country": "Mexico"},
    {"id": 2282, "name": "Tigres UANL", "country": "Mexico"},
    {"id": 2283, "name": "Monterrey", "country": "Mexico"},
    {"id": 2284, "name": "León", "country": "Mexico"},
    {"id": 2285, "name": "Pachuca", "country": "Mexico"},
    {"id": 2286, "name": "Toluca", "country": "Mexico"},
    {"id": 2287, "name": "Santos Laguna", "country": "Mexico"},
    {"id": 2288, "name": "Atlas", "country": "Mexico"},
    {"id": 2289, "name": "Puebla", "country": "Mexico"},
    {"id": 2290, "name": "Mazatlán", "country": "Mexico"},
    {"id": 2291, "name": "Juárez", "country": "Mexico"},
    {"id": 2292, "name": "Querétaro", "country": "Mexico"},
    {"id": 2293, "name": "San Luis", "country": "Mexico"},
    {"id": 2294, "name": "Necaxa", "country": "Mexico"},
    {"id": 2295, "name": "Tijuana", "country": "Mexico"},
]

# ============================================
# MLS - Estados Unidos
# ============================================
equipos_mls = [
    {"id": 1608, "name": "Inter Miami", "country": "USA"},
    {"id": 1609, "name": "LAFC", "country": "USA"},
    {"id": 1610, "name": "LA Galaxy", "country": "USA"},
    {"id": 1611, "name": "New York City FC", "country": "USA"},
    {"id": 1612, "name": "New York Red Bulls", "country": "USA"},
    {"id": 1613, "name": "Atlanta United", "country": "USA"},
    {"id": 1614, "name": "Seattle Sounders", "country": "USA"},
    {"id": 1615, "name": "Portland Timbers", "country": "USA"},
    {"id": 1616, "name": "Philadelphia Union", "country": "USA"},
    {"id": 1617, "name": "Columbus Crew", "country": "USA"},
    {"id": 1618, "name": "FC Cincinnati", "country": "USA"},
    {"id": 1619, "name": "Orlando City", "country": "USA"},
    {"id": 1620, "name": "Chicago Fire", "country": "USA"},
    {"id": 1621, "name": "New England Revolution", "country": "USA"},
    {"id": 1622, "name": "Toronto FC", "country": "Canada"},
    {"id": 1623, "name": "Vancouver Whitecaps", "country": "Canada"},
    {"id": 1624, "name": "CF Montréal", "country": "Canada"},
    {"id": 1625, "name": "Minnesota United", "country": "USA"},
    {"id": 1626, "name": "Sporting Kansas City", "country": "USA"},
    {"id": 1627, "name": "Real Salt Lake", "country": "USA"},
    {"id": 1628, "name": "Colorado Rapids", "country": "USA"},
    {"id": 1629, "name": "FC Dallas", "country": "USA"},
    {"id": 1630, "name": "Houston Dynamo", "country": "USA"},
    {"id": 1631, "name": "Austin FC", "country": "USA"},
    {"id": 1632, "name": "San Jose Earthquakes", "country": "USA"},
    {"id": 1633, "name": "Nashville SC", "country": "USA"},
    {"id": 1634, "name": "Charlotte FC", "country": "USA"},
    {"id": 1635, "name": "St. Louis City", "country": "USA"},
]

# ============================================
# CENTROAMÉRICA
# ============================================
equipos_centroamerica = [
    # Costa Rica
    {"id": 1801, "name": "Saprissa", "country": "Costa Rica"},
    {"id": 1802, "name": "Alajuelense", "country": "Costa Rica"},
    {"id": 1803, "name": "Herediano", "country": "Costa Rica"},
    {"id": 1804, "name": "Cartaginés", "country": "Costa Rica"},
    
    # Honduras
    {"id": 1811, "name": "Olimpia", "country": "Honduras"},
    {"id": 1812, "name": "Motagua", "country": "Honduras"},
    {"id": 1813, "name": "Real España", "country": "Honduras"},
    {"id": 1814, "name": "Marathón", "country": "Honduras"},
    
    # Guatemala
    {"id": 1821, "name": "Municipal", "country": "Guatemala"},
    {"id": 1822, "name": "Comunicaciones", "country": "Guatemala"},
    {"id": 1823, "name": "Antigua GFC", "country": "Guatemala"},
    {"id": 1824, "name": "Xelajú", "country": "Guatemala"},
    
    # Panamá
    {"id": 1831, "name": "Tauro", "country": "Panama"},
    {"id": 1832, "name": "Árabe Unido", "country": "Panama"},
    {"id": 1833, "name": "Plaza Amador", "country": "Panama"},
    {"id": 1834, "name": "Independiente", "country": "Panama"},
    
    # El Salvador
    {"id": 1841, "name": "Águila", "country": "El Salvador"},
    {"id": 1842, "name": "FAS", "country": "El Salvador"},
    {"id": 1843, "name": "Alianza", "country": "El Salvador"},
    {"id": 1844, "name": "Isidro Metapán", "country": "El Salvador"},
]

# ============================================
# CARIBE
# ============================================
equipos_caribe = [
    # Jamaica
    {"id": 1851, "name": "Portmore United", "country": "Jamaica"},
    {"id": 1852, "name": "Waterhouse", "country": "Jamaica"},
    {"id": 1853, "name": "Mount Pleasant", "country": "Jamaica"},
    {"id": 1854, "name": "Cavalier", "country": "Jamaica"},
    
    # Trinidad y Tobago
    {"id": 1861, "name": "Defence Force", "country": "Trinidad and Tobago"},
    {"id": 1862, "name": "W Connection", "country": "Trinidad and Tobago"},
    {"id": 1863, "name": "Central FC", "country": "Trinidad and Tobago"},
    {"id": 1864, "name": "Police FC", "country": "Trinidad and Tobago"},
    
    # República Dominicana
    {"id": 1871, "name": "Cibao", "country": "Dominican Republic"},
    {"id": 1872, "name": "Moca", "country": "Dominican Republic"},
    {"id": 1873, "name": "Atlántico", "country": "Dominican Republic"},
    
    # Haití
    {"id": 1881, "name": "Violette", "country": "Haiti"},
    {"id": 1882, "name": "Arcahaie", "country": "Haiti"},
    {"id": 1883, "name": "Don Bosco", "country": "Haiti"},
]

# Agrupar todos los equipos de CONCACAF
todos_concacaf = []
todos_concacaf.extend(equipos_mexico)
todos_concacaf.extend(equipos_mls)
todos_concacaf.extend(equipos_centroamerica)
todos_concacaf.extend(equipos_caribe)

print(f"📊 Total equipos CONCACAF a agregar: {len(todos_concacaf)}")

# Cargar base de datos actual
db_file = "data/teams_database.json"
with open(db_file, 'r') as f:
    db = json.load(f)

print(f"✅ Base actual cargada: {db.get('total_teams', 0)} equipos")

# Verificar estructura
if isinstance(db, list):
    print("⚠️ Convirtiendo de lista a diccionario...")
    new_db = {
        "total_teams": len(db),
        "indexes": {"by_name": {}},
        "teams": {}
    }
    for team in db:
        if isinstance(team, dict) and 'id' in team:
            team_id = str(team['id'])
            new_db['teams'][team_id] = team
            new_db['indexes']['by_name'][team['name'].lower()] = team_id
    db = new_db

# Agregar equipos
agregados = 0
duplicados = 0

print("\n📝 Agregando equipos CONCACAF:")
for equipo in todos_concacaf:
    team_id = str(equipo['id'])
    team_name = equipo['name']
    
    if team_id in db.get('teams', {}):
        print(f"   ⏭️  {team_name} ya existe")
        duplicados += 1
        continue
    
    # Agregar a teams
    if 'teams' not in db:
        db['teams'] = {}
    db['teams'][team_id] = equipo
    
    # Agregar a índices
    if 'indexes' not in db:
        db['indexes'] = {'by_name': {}}
    if 'by_name' not in db['indexes']:
        db['indexes']['by_name'] = {}
    
    name_lower = team_name.lower()
    db['indexes']['by_name'][name_lower] = team_id
    
    # Variantes comunes
    if ' ' in name_lower:
        db['indexes']['by_name'][name_lower.replace(' ', '')] = team_id
    
    # Variantes específicas para equipos mexicanos
    if 'america' in name_lower:
        db['indexes']['by_name']['club america'] = team_id
        db['indexes']['by_name']['las aguilas'] = team_id
    elif 'guadalajara' in name_lower:
        db['indexes']['by_name']['chivas'] = team_id
    elif 'cruz azul' in name_lower:
        db['indexes']['by_name']['la maquina'] = team_id
    elif 'pumas' in name_lower:
        db['indexes']['by_name']['unam'] = team_id
    elif 'tigres' in name_lower:
        db['indexes']['by_name']['uanl'] = team_id
    elif 'monterrey' in name_lower:
        db['indexes']['by_name']['rayados'] = team_id
    
    print(f"   ✅ {team_name} ({equipo['country']})")
    agregados += 1

# Actualizar total
db['total_teams'] = len(db.get('teams', {}))

# Guardar cambios
backup_file = "data/teams_database_backup_concacaf.json"
if os.path.exists(db_file):
    os.rename(db_file, backup_file)
    print(f"\n✅ Backup guardado: {backup_file}")

with open(db_file, 'w') as f:
    json.dump(db, f, indent=2)

print("\n" + "=" * 70)
print("📊 RESUMEN FINAL")
print("=" * 70)
print(f"✅ Equipos CONCACAF agregados: {agregados}")
print(f"⏭️  Equipos duplicados: {duplicados}")
print(f"📊 Total equipos en base: {db['total_teams']}")
print(f"📊 Total índices: {len(db.get('indexes', {}).get('by_name', {}))}")

# Verificar equipos clave
print("\n🔍 VERIFICANDO EQUIPOS CLAVE DE CONCACAF:")
from modules.team_database import TeamDatabase
db_check = TeamDatabase()

equipos_concacaf = [
    'América', 'Guadalajara', 'Cruz Azul', 'Pumas UNAM', 'Tigres UANL', 'Monterrey',
    'Inter Miami', 'LAFC', 'LA Galaxy', 'Seattle Sounders',
    'Saprissa', 'Alajuelense', 'Olimpia', 'Municipal', 'Tauro',
    'Portmore United', 'Cibao', 'Violette'
]

for equipo in equipos_concacaf:
    team_id = db_check.get_team_id(equipo)
    if team_id:
        print(f"  ✅ {equipo}: ID {team_id}")
    else:
        print(f"  ❌ {equipo}: No encontrado")
