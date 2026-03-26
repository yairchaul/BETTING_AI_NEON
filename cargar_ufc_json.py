# -*- coding: utf-8 -*-
"""
CARGAR UFC DESDE JSON - Usa tu archivo eventos_ufc.json existente
"""

import sqlite3
import json

def cargar_ufc_desde_json():
    """Carga eventos y peleadores desde eventos_ufc.json"""
    
    # Leer archivo JSON
    try:
        with open("eventos_ufc.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error leyendo eventos_ufc.json: {e}")
        return
    
    conn = sqlite3.connect("data/betting_stats.db")
    cursor = conn.cursor()
    
    total_combates = 0
    
    for fecha, evento in data.items():
        nombre = evento.get("nombre", "UFC Event")
        combates = evento.get("combates", [])
        
        # Guardar evento
        cursor.execute('''
            INSERT OR REPLACE INTO eventos_ufc (nombre, fecha, cartelera)
            VALUES (?, ?, ?)
        ''', (nombre, fecha, json.dumps(combates, ensure_ascii=False)))
        
        # Guardar peleadores
        for c in combates:
            p1_nombre = c.get("peleador1")
            p2_nombre = c.get("peleador2")
            p1_record = c.get("record1", "0-0-0")
            p2_record = c.get("record2", "0-0-0")
            metodo = c.get("metodo", "")
            
            # Guardar peleador 1
            cursor.execute('''
                INSERT OR IGNORE INTO peleadores_ufc (nombre, record)
                VALUES (?, ?)
            ''', (p1_nombre, p1_record))
            
            # Guardar peleador 2
            cursor.execute('''
                INSERT OR IGNORE INTO peleadores_ufc (nombre, record)
                VALUES (?, ?)
            ''', (p2_nombre, p2_record))
            
            total_combates += 1
        
        print(f"✅ {nombre} ({fecha}) - {len(combates)} combates")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ UFC cargado correctamente:")
    print(f"   - {total_combates} combates cargados")
    print(f"   - {len(data)} eventos en BD")

if __name__ == "__main__":
    cargar_ufc_desde_json()
