#!/usr/bin/env python3
"""
Análisis completo de las capturas de Caliente.mx - 6 Marzo 2026
"""
from modules.team_database import TeamDatabase
from modules.smart_betting_ai import SmartBettingAI
from modules.parlay_reasoning_engine import ParlayReasoningEngine
import json
from datetime import datetime

def cuota_a_probabilidad(cuota):
    """Convierte cuota americana a probabilidad implícita"""
    cuota = str(cuota)
    if cuota.startswith('+'):
        prob = 100 / (float(cuota[1:]) + 100)
    elif cuota.startswith('-'):
        prob = float(cuota[1:]) / (float(cuota[1:]) + 100)
    else:
        prob = 1 / float(cuota)
    return round(prob, 3)

def analizar_partido(local, visitante, cuota_local, cuota_empate, cuota_visitante, db):
    """Analiza un partido y devuelve recomendaciones"""
    print(f"\n{'='*60}")
    print(f"⚽ {local} vs {visitante}")
    print(f"{'='*60}")
    
    local_id = db.get_team_id(local)
    visitante_id = db.get_team_id(visitante)
    
    if not local_id:
        print(f"❌ ERROR: {local} no encontrado en base de datos")
        return None
    if not visitante_id:
        print(f"❌ ERROR: {visitante} no encontrado en base de datos")
        return None
    
    print(f"✅ IDs: {local}={local_id}, {visitante}={visitante_id}")
    
    # Convertir cuotas a probabilidades
    prob_local = cuota_a_probabilidad(cuota_local)
    prob_empate = cuota_a_probabilidad(cuota_empate)
    prob_visitante = cuota_a_probabilidad(cuota_visitante)
    
    print(f"\n📊 PROBABILIDADES IMPLÍCITAS:")
    print(f"   {local}: {prob_local:.1%} (cuota {cuota_local})")
    print(f"   Empate: {prob_empate:.1%} (cuota {cuota_empate})")
    print(f"   {visitante}: {prob_visitante:.1%} (cuota {cuota_visitante})")
    
    # Determinar favorito
    if prob_local > prob_visitante and prob_local > prob_empate:
        favorito = local
        prob_favorito = prob_local
        underdog = visitante
        print(f"\n🏆 Favorito: {favorito}")
    elif prob_visitante > prob_local and prob_visitante > prob_empate:
        favorito = visitante
        prob_favorito = prob_visitante
        underdog = local
        print(f"\n🏆 Favorito: {favorito}")
    else:
        print(f"\n⚖️ Partido equilibrado")
        favorito = None
        prob_favorito = 0
    
    # Aplicar reglas jerárquicas
    print(f"\n📋 REGLAS JERÁRQUICAS:")
    
    # Nivel 1 - Over 1.5 Primer Tiempo (simulado)
    prob_over15_ht = 0.45  # Esto vendría del modelo
    if prob_over15_ht > 0.50:
        print(f"   ✅ Nivel 1: Over 1.5 1T ({prob_over15_ht:.1%})")
    else:
        print(f"   ❌ Nivel 1: Over 1.5 1T ({prob_over15_ht:.1%})")
        
        # Nivel 2 - BTTS (simulado)
        prob_btts = 0.52
        if prob_btts > 0.50:
            print(f"   ✅ Nivel 2: BTTS Sí ({prob_btts:.1%})")
        else:
            print(f"   ❌ Nivel 2: BTTS Sí ({prob_btts:.1%})")
    
    return {
        'partido': f"{local} vs {visitante}",
        'local': local,
        'visitante': visitante,
        'cuotas': {
            'local': cuota_local,
            'empate': cuota_empate,
            'visitante': cuota_visitante
        },
        'probabilidades': {
            'local': prob_local,
            'empate': prob_empate,
            'visitante': prob_visitante
        },
        'favorito': favorito
    }

def main():
    print("🎯 ANÁLISIS DE CAPTURAS CALIENTE.MX")
    print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 60)
    
    db = TeamDatabase()
    
    # Partidos de tus capturas
    partidos = [
        # Eredivisie
        ("Heracles Almelo", "Utrecht", "+215", "+245", "+120"),
        ("Groningen", "Ajax Amsterdam", "+166", "+270", "+142"),
        ("PSV Eindhoven", "AZ Alkmaar", "-334", "+500", "+710"),
        ("Excelsior", "Heerenveen", "+182", "+265", "+130"),
        ("Sparta Rotterdam", "Zwolle", "-150", "+310", "+355"),
        
        # LaLiga
        ("Celta de Vigo", "Real Madrid", "+220", "+230", "+126"),
        
        # Ligue 1
        ("Paris Saint Germain", "AS Monaco", "-286", "+450", "+620"),
        
        # Serie A
        ("Napoli", "Torino", "-179", "+290", "+520"),
        
        # Bundesliga
        ("Bayern Munich", "Borussia Mönchengladbach", "-455", "+625", "+880"),
    ]
    
    resultados = []
    for local, visitante, cl, ce, cv in partidos:
        resultado = analizar_partido(local, visitante, cl, ce, cv, db)
        if resultado:
            resultados.append(resultado)
    
    # Resumen de favoritos
    print("\n" + "="*60)
    print("📊 RESUMEN DE FAVORITOS")
    print("="*60)
    for r in resultados:
        if r['favorito']:
            print(f"• {r['partido']}: {r['favorito']}")
        else:
            print(f"• {r['partido']}: EQUILIBRADO")

if __name__ == "__main__":
    main()
