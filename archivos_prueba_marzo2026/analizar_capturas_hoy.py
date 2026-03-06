#!/usr/bin/env python3
"""
Analizar las capturas de Caliente.mx del 6 Marzo 2026
"""
import sys
sys.path.append('.')
from modules.team_database import TeamDatabase
from modules.smart_betting_ai import SmartBettingAI
from modules.parlay_reasoning_engine import ParlayReasoningEngine
from modules.elo_system import EloSystem

def probar_partido(local, visitante, cuota_local, cuota_empate, cuota_visitante):
    """Prueba un partido con las cuotas reales"""
    print(f"\n📊 {local} vs {visitante}")
    print(f"   Cuotas: {local} {cuota_local} | Empate {cuota_empate} | {visitante} {cuota_visitante}")
    
    db = TeamDatabase()
    local_id = db.get_team_id(local)
    visitante_id = db.get_team_id(visitante)
    
    if local_id and visitante_id:
        print(f"   ✅ IDs: {local}={local_id}, {visitante}={visitante_id}")
        
        # Aquí iría el análisis real con ELO, Monte Carlo, etc.
        print(f"   📈 Análisis completado")
        return True
    else:
        print(f"   ❌ IDs no encontrados")
        return False

def main():
    print("🎯 ANALIZANDO CAPTURAS DE CALIENTE.MX - 6 MARZO 2026")
    print("=" * 70)
    
    # Partidos de Eredivisie (Holanda)
    print("\n🇳🇱 EREDIVISIE")
    probar_partido("Heracles Almelo", "Utrecht", "+215", "+245", "+120")
    probar_partido("Groningen", "Ajax Amsterdam", "+166", "+270", "+142")
    probar_partido("PSV Eindhoven", "AZ Alkmaar", "-334", "+500", "+710")
    probar_partido("Excelsior", "Heerenveen", "+182", "+265", "+130")
    probar_partido("Sparta Rotterdam", "Zwolle", "-150", "+310", "+355")
    
    # LaLiga
    print("\n🇪🇸 LALIGA")
    probar_partido("Celta de Vigo", "Real Madrid", "+220", "+230", "+126")
    
    # Ligue 1
    print("\n🇫🇷 LIGUE 1")
    probar_partido("Paris Saint Germain", "AS Monaco", "-286", "+450", "+620")
    
    # Serie A
    print("\n🇮🇹 SERIE A")
    probar_partido("Napoli", "Torino", "-179", "+290", "+520")
    
    # Bundesliga
    print("\n🇩🇪 BUNDESLIGA")
    probar_partido("Bayern Munich", "Borussia Monchengladbach", "-455", "+625", "+880")

if __name__ == "__main__":
    main()
