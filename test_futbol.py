"""
Prueba rápida del procesador de fútbol
"""
import sys
from processors.procesador_futbol import ProcesadorFutbol

# Texto de prueba con los partidos de tu captura
texto_prueba = """
Bayer Leverkusen +490 Empate +320 Arsenal -186
Real Madrid +260 Empate +265 Manchester City -104
Bodo Glimt +125 Empate +255 Sporting Lisboa +200
PSG -105 Empate +275 Chelsea +250
Barcelona -176 Empate +355 Newcastle +400
Liverpool -371 Empate +500 Galatasaray +850
Tottenham +152 Empate +275 Atlético Madrid +152
Bayern Munich -385 Empate +490 Atalanta +925
"""

print("="*60)
print("🧪 PRUEBA PROCESADOR FÚTBOL")
print("="*60)

# Crear procesador
procesador = ProcesadorFutbol()

# Procesar texto
eventos = procesador.procesar(texto_prueba)

print(f"\n📊 Total eventos detectados: {len(eventos)}")
print("\n" + "="*60)
print("📋 DETALLE DE EVENTOS:")
print("="*60)

for i, evento in enumerate(eventos, 1):
    print(f"\n{i}. {evento.equipo_local} vs {evento.equipo_visitante}")
    print(f"   📍 Local: {evento.odds_local:.2f} (decimal)")
    print(f"   🤝 Empate: {evento.odds_empate:.2f} (decimal)")
    print(f"   🛣️ Visitante: {evento.odds_visitante:.2f} (decimal)")
    
    # Verificar conversión correcta
    print(f"   📊 Verificación:")
    print(f"      - Probabilidad local: {1/evento.odds_local*100:.1f}%")
    print(f"      - Probabilidad empate: {1/evento.odds_empate*100:.1f}%")
    print(f"      - Probabilidad visitante: {1/evento.odds_visitante*100:.1f}%")
    print(f"      - Suma: {(1/evento.odds_local + 1/evento.odds_empate + 1/evento.odds_visitante)*100:.1f}%")

print("\n" + "="*60)
print("✅ PRUEBA COMPLETADA")
print("="*60)
