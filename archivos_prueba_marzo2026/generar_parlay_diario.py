#!/usr/bin/env python3
"""
Genera parlays automáticamente cada día
"""
from modules.team_database import TeamDatabase
from modules.smart_betting_ai import SmartBettingAI
from modules.parlay_generator import build_parlay
import json
from datetime import datetime

def generar_parlays():
    print(f"📊 GENERANDO PARLAYS - {datetime.now().strftime('%d/%m/%Y')}")
    print("=" * 60)
    
    db = TeamDatabase()
    ai = SmartBettingAI()
    
    # Partidos del día (esto vendría de una API)
    partidos = [
        ("Tottenham", "Arsenal"),
        ("Liverpool", "Manchester United"),
        ("Real Madrid", "Barcelona")
    ]
    
    picks_parlay = []
    
    for local, visitante in partidos:
        print(f"\n📊 {local} vs {visitante}")
        
        # Obtener predicciones del sistema de reglas
        prediccion = ai.analizar_partido(local, visitante)
        
        if prediccion and prediccion['probabilidad'] >= 0.50:
            print(f"  ✅ Pick: {prediccion['mercado']} ({prediccion['probabilidad']:.1%})")
            picks_parlay.append({
                "partido": f"{local} vs {visitante}",
                "pick": prediccion['mercado'],
                "prob": prediccion['probabilidad'],
                "odds": prediccion['cuota']
            })
        else:
            print(f"  ❌ Sin pick válido (prob < 50%)")
    
    # Construir parlay si hay suficientes picks
    if len(picks_parlay) >= 2:
        parlay = build_parlay(picks_parlay)
        print(f"\n🎯 PARLAY GENERADO:")
        print(f"   Probabilidad: {parlay['probability']:.1%}")
        print(f"   Cuota total: {parlay['odds']:.2f}")
        print(f"   Valor esperado: {parlay['expected_value']:.2%}")
        
        # Guardar para histórico
        with open(f"data/parlays/{datetime.now().strftime('%Y%m%d')}.json", 'w') as f:
            json.dump({
                "fecha": datetime.now().isoformat(),
                "picks": picks_parlay,
                "parlay": parlay
            }, f, indent=2)
    else:
        print("\n❌ No hay suficientes picks para parlay")

if __name__ == "__main__":
    generar_parlays()
