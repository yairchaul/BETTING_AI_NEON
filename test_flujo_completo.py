"""
Script de prueba para verificar el flujo completo
"""
from processors.vision_reader import VisionReader

print("="*60)
print("🧪 PRUEBA COMPLETA: VisionReader + StatsEngine + RuleEngine")
print("="*60)

# Crear vision reader
v = VisionReader()

# Procesar captura simulada
eventos = v.procesar_captura('test.png')

print(f"\n📊 Total eventos detectados: {len(eventos)}")
print("="*60)

# Mostrar cada evento con sus picks
for i, e in enumerate(eventos, 1):
    print(f"\n{i}. {e.equipo_local} vs {e.equipo_visitante}")
    print(f"   📍 Local: {e.odds_local:.2f} | 🤝 Empate: {e.odds_empate:.2f} | 🛣️ Visitante: {e.odds_visitante:.2f}")
    
    if hasattr(e, 'value_bets') and e.value_bets:
        print(f"   🎯 Picks ({len(e.value_bets)}):")
        for pick in e.value_bets:
            nivel = pick.get('nivel', '?')
            desc = pick.get('descripcion', pick.get('mercado', 'Unknown'))
            prob = pick.get('probabilidad', 0) * 100
            odds = pick.get('odds', 0)
            print(f"      Nivel {nivel}: {desc} - {prob:.1f}% @ {odds:.2f}")
    else:
        print("   ⚠️ Sin picks detectados")
    
    print("-" * 40)

print("\n✅ Prueba completada")
