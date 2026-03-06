#!/usr/bin/env python3
"""
Registrar parlays manualmente en el sistema
"""
import json
from datetime import datetime
from modules.parlay_reasoning_engine import ParlayReasoningEngine

def registrar_parlay():
    print("🎯 REGISTRAR PARLAY MANUALMENTE")
    print("=" * 60)
    
    parlays = []
    
    while True:
        print("\n📝 NUEVO PARLAY")
        partido = input("Partido (ej: América vs Chivas): ")
        mercado = input("Mercado (ej: Over 1.5, BTTS Sí, Gana América): ")
        prob = float(input("Probabilidad (0-1): "))
        odds = float(input("Cuota: "))
        
        parlays.append({
            'partido': partido,
            'mercado': mercado,
            'prob': prob,
            'odds': odds,
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M')
        })
        
        otro = input("\n¿Agregar otro pick? (s/n): ")
        if otro.lower() != 's':
            break
    
    if len(parlays) >= 2:
        # Calcular parlay
        engine = ParlayReasoningEngine()
        prob_total = 1.0
        odds_total = 1.0
        
        for pick in parlays:
            prob_total *= pick['prob']
            odds_total *= pick['odds']
        
        ev = (prob_total * odds_total) - 1
        
        print("\n" + "=" * 60)
        print("🎯 PARLAY REGISTRADO")
        print("=" * 60)
        for pick in parlays:
            print(f"• {pick['partido']}: {pick['mercado']} ({pick['prob']:.0%}) @ {pick['odds']}")
        print(f"\n📊 Probabilidad total: {prob_total:.2%}")
        print(f"💰 Cuota total: {odds_total:.2f}")
        print(f"📈 Valor esperado: {ev:.2%}")
        
        # Guardar en archivo
        filename = f"data/parlays/parlay_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        import os
        os.makedirs("data/parlays", exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump({
                'fecha': datetime.now().isoformat(),
                'picks': parlays,
                'probabilidad_total': prob_total,
                'odds_total': odds_total,
                'ev': ev
            }, f, indent=2)
        
        print(f"\n✅ Guardado en: {filename}")
    else:
        print("❌ Se necesitan al menos 2 picks para un parlay")

if __name__ == "__main__":
    registrar_parlay()
