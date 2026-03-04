# test_elo_real.py
from modules.elo_system import ELOSystem

print(' PRUEBA REAL DE ELO')
print('=' * 60)

elo = ELOSystem()

# Cargar ratings existentes si hay
try:
    elo.load_ratings()
    print(' Ratings cargados')
except:
    print(' Creando nuevos ratings')

# Probar con equipos mexicanos
equipos = ['Puebla', 'Tigres UANL', 'Monterrey', 'América', 'Chivas', 'Cruz Azul']

print('\n RATINGS ACTUALES:')
for equipo in equipos:
    rating = elo.get_rating(equipo)
    print(f'   {equipo}: {rating:.0f}')

# Simular partidos pasados para ajustar ratings
print('\n Simulando partidos recientes...')
resultados = [
    ('Monterrey', 'Tigres UANL', 2, 1),
    ('América', 'Chivas', 1, 1),
    ('Cruz Azul', 'Puebla', 2, 0),
]

for home, away, gh, ga in resultados:
    elo.update_ratings(home, away, gh, ga)
    print(f'   {home} {gh}-{ga} {away}')

print('\n RATINGS ACTUALIZADOS:')
for equipo in equipos:
    rating = elo.get_rating(equipo)
    print(f'   {equipo}: {rating:.0f}')

# Probabilidades para Puebla vs Tigres
print('\n PROBABILIDADES Puebla vs Tigres:')
probs = elo.get_win_probability('Puebla', 'Tigres UANL')
print(f'   Local: {probs["home"]:.1%}')
print(f'   Empate: {probs["draw"]:.1%}')
print(f'   Visitante: {probs["away"]:.1%}')
