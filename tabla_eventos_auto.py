# -*- coding: utf-8 -*-
"""
INICIALIZADOR AUTOMÁTICO DE EVENTOS UFC
Extrae la cartelera real según la fecha actual.
"""
import sqlite3
import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def extraer_cartelera_actual():
    """Busca en la web oficial el próximo evento y sus peleadores"""
    print("🔍 Buscando cartelera real en UFC.com...")
    url = "https://www.ufcespanol.com/events"
    
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'lxml')
        
        evento_link = soup.select_one(".c-card-event--result__headline a")
        if not evento_link:
            print("❌ No se encontró evento")
            return None, []
            
        nombre_evento = evento_link.text.strip()
        link_detalle = "https://www.ufcespanol.com" + evento_link['href']
        
        res_detalle = requests.get(link_detalle, timeout=10)
        soup_detalle = BeautifulSoup(res_detalle.text, 'lxml')
        
        peleas = []
        items = soup_detalle.select(".c-listing-fight")
        
        for item in items:
            try:
                p1 = item.select_one(".c-listing-fight__corner-name--red")
                p2 = item.select_one(".c-listing-fight__corner-name--blue")
                if p1 and p2:
                    peleas.append({
                        "peleador1": p1.get_text(separator=" ").strip(),
                        "record1": "0-0-0",
                        "peleador2": p2.get_text(separator=" ").strip(),
                        "record2": "0-0-0"
                    })
            except:
                continue
                
        return nombre_evento, peleas
    except Exception as e:
        print(f"❌ Error en el scraping: {e}")
        return None, []

def inicializar_bd():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect("data/betting_stats.db")
    cursor = conn.cursor()
    
    # Tabla de eventos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS eventos_ufc (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            fecha TEXT,
            cartelera TEXT,
            ultima_actualizacion TEXT
        )
    ''')
    
    # Tabla de peleadores mejorada (con tipos REAL)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS peleadores_ufc (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE,
            record TEXT,
            altura REAL,
            peso REAL,
            alcance REAL,
            postura TEXT,
            ko_rate REAL,
            grappling REAL,
            strikes_por_min REAL,
            defensa_strikes REAL,
            odds TEXT,
            ultima_actualizacion TEXT
        )
    ''')
    conn.commit()
    return conn

def ejecutar_actualizacion():
    conn = inicializar_bd()
    nombre_ev, cartelera = extraer_cartelera_actual()
    
    if nombre_ev and cartelera:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM eventos_ufc")
        
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        cursor.execute('''
            INSERT INTO eventos_ufc (nombre, fecha, cartelera, ultima_actualizacion)
            VALUES (?, ?, ?, ?)
        ''', (nombre_ev, fecha_hoy, json.dumps(cartelera, ensure_ascii=False), datetime.now().isoformat()))
        
        conn.commit()
        print(f"✅ Actualizado: {nombre_ev} ({len(cartelera)} peleas)")
    else:
        print("⚠️ No se pudo automatizar, verifica conexión")
    
    conn.close()

if __name__ == "__main__":
    ejecutar_actualizacion()
