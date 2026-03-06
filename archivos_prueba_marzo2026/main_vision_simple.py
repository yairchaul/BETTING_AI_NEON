#!/usr/bin/env python3
"""
Versión simplificada de main_vision.py para pruebas
"""
import sys
import json
from modules.team_database import TeamDatabase
from modules.hybrid_data_provider import HybridDataProvider
from modules.smart_betting_ai import SmartBettingAI

def main():
    print("🔍 EJECUTANDO ANÁLISIS DE PARTIDOS")
    print("=" * 60)
    
    # Procesar argumentos
    umbral = 50
    if len(sys.argv) > 2 and sys.argv[1] == "--umbral":
        umbral = int(sys.argv[2])
        print(f"📊 Usando umbral: {umbral}%")
    
    # Cargar base de datos
    db = TeamDatabase()
    if not db.data:
        print("❌ No se pudo cargar la base de datos")
        return
    
    # Probar con algunos partidos
    partidos = [
        ("Tottenham", "Arsenal"),
        ("Real Madrid", "Barcelona"),
        ("Liverpool", "Manchester United"),
        ("Cienciano", "Melgar"),
        ("Bucaramanga", "America de Cali")
    ]
    
    for local, visitante in partidos:
        print(f"\n📊 {local} vs {visitante}")
        print("-" * 40)
        
        # Obtener IDs
        local_id = db.get_team_id(local)
        visitante_id = db.get_team_id(visitante)
        
        if local_id and visitante_id:
            print(f"  ✅ IDs encontrados: {local}={local_id}, {visitante}={visitante_id}")
            
            # Aquí iría la lógica de predicción
            print(f"  📈 Análisis completado (umbral {umbral}%)")
        else:
            print(f"  ❌ No se encontraron IDs:")
            if not local_id:
                print(f"     - {local}: No encontrado")
            if not visitante_id:
                print(f"     - {visitante}: No encontrado")
    
    print("\n" + "=" * 60)
    print("✅ ANÁLISIS COMPLETADO")

if __name__ == "__main__":
    main()
