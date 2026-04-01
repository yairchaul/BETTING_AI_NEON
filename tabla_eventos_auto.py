# -*- coding: utf-8 -*-
"""
INICIALIZADOR AUTOMÁTICO DE EVENTOS UFC - Versión Robusta
Extrae la cartelera real desde ufcespanol.com/events
"""

import sqlite3
import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def extraer_cartelera_actual():
    """
    Extrae la cartelera real desde ufcespanol.com/events
    Basado en la estructura real de la página
    """
    print("🔍 Buscando cartelera real en UFC Español...")
    url = "https://www.ufcespanol.com/events"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, timeout=12, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar el próximo evento - según la estructura real
        # El evento principal está en .c-card-event--result
        evento_principal = soup.select_one('.c-card-event--result')
        
        if not evento_principal:
            print("⚠️ No se encontró evento principal")
            return None, []
        
        # Extraer nombre del evento
        nombre_evento = "UFC Fight Night"
        nombre_tag = evento_principal.select_one('.c-card-event--result__headline')
        if nombre_tag:
            nombre_texto = nombre_tag.get_text(strip=True)
            # Limpiar texto
            nombre_evento = re.sub(r'\s+', ' ', nombre_texto).strip()
        
        # Extraer fecha
        fecha_tag = evento_principal.select_one('.c-card-event--result__date')
        fecha_evento = datetime.now().strftime("%Y-%m-%d")
        if fecha_tag:
            fecha_texto = fecha_tag.get_text(strip=True)
            # Intentar extraer fecha
            fecha_match = re.search(r'(\d{1,2})\s+de\s+(\w+)', fecha_texto, re.IGNORECASE)
            if fecha_match:
                dia = fecha_match.group(1)
                mes = fecha_match.group(2)
                meses = {
                    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
                    'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
                }
                mes_num = meses.get(mes.lower(), datetime.now().month)
                fecha_evento = f"{datetime.now().year}-{mes_num:02d}-{int(dia):02d}"
        
        # Buscar link al detalle del evento
        link_tag = evento_principal.select_one('a')
        link_detalle = link_tag.get('href') if link_tag else None
        if link_detalle and not link_detalle.startswith('http'):
            link_detalle = "https://www.ufcespanol.com" + link_detalle
        
        # Extraer peleas - buscar en la página principal o en el detalle
        peleas = []
        
        # Primero intentar extraer desde la página principal
        items = soup.select('.c-listing-fight')
        
        if not items and link_detalle:
            # Intentar obtener desde el detalle del evento
            try:
                res_detalle = requests.get(link_detalle, timeout=10, headers=headers)
                soup_detalle = BeautifulSoup(res_detalle.text, 'html.parser')
                items = soup_detalle.select('.c-listing-fight')
            except Exception as e:
                print(f"⚠️ No se pudo obtener detalle: {e}")
        
        for item in items[:10]:  # máximo 10 peleas
            try:
                # Buscar nombres de peleadores
                p1_tag = item.select_one('.c-listing-fight__corner-name--red, .fighter-name')
                p2_tag = item.select_one('.c-listing-fight__corner-name--blue, .fighter-name')
                
                if p1_tag and p2_tag:
                    p1 = p1_tag.get_text(strip=True)
                    p2 = p2_tag.get_text(strip=True)
                    if p1 and p2:
                        peleas.append({
                            "peleador1": p1,
                            "record1": "0-0-0",
                            "peleador2": p2,
                            "record2": "0-0-0"
                        })
            except Exception as e:
                continue
        
        # Si no se encontraron peleas, usar información de la página principal
        if not peleas:
            # Buscar peleadores en la página principal
            fighter_links = soup.select('a[href*="/athlete/"]')
            nombres = []
            for link in fighter_links:
                nombre = link.get_text(strip=True)
                if nombre and len(nombre) > 3:
                    nombres.append(nombre)
            
            # Agrupar de a dos
            for i in range(0, len(nombres), 2):
                if i + 1 < len(nombres):
                    peleas.append({
                        "peleador1": nombres[i],
                        "record1": "0-0-0",
                        "peleador2": nombres[i+1],
                        "record2": "0-0-0"
                    })
        
        if peleas:
            print(f"✅ Evento encontrado: {nombre_evento}")
            print(f"📅 Fecha: {fecha_evento}")
            print(f"🥊 Peleas: {len(peleas)}")
            return nombre_evento, peleas
        else:
            print("⚠️ No se encontraron peleas en la cartelera")
            return None, []
            
    except Exception as e:
        print(f"❌ Error extrayendo cartelera: {e}")
        return None, []


def extraer_cartelera_fallback():
    """Fallback con datos de la cartelera real (Moicano vs Duncan)"""
    print("📋 Usando fallback con cartelera real actual...")
    
    nombre_evento = "UFC Vegas 115: Moicano vs. Duncan"
    peleas = [
        {"peleador1": "Renato Moicano", "record1": "19-5-1", "peleador2": "Grant Duncan", "record2": "12-3-0"},
        {"peleador1": "Mickey Gall", "record1": "7-5-0", "peleador2": "Mike Malott", "record2": "10-2-1"},
        {"peleador1": "Brendan Allen", "record1": "24-5-0", "peleador2": "Andre Muniz", "record2": "23-5-0"},
        {"peleador1": "Bruna Brasil", "record1": "11-6-1", "peleador2": "Alexia Thainara", "record2": "13-1-0"},
    ]
    return nombre_evento, peleas


def inicializar_bd():
    """Inicializa la base de datos"""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect("data/betting_stats.db")
    cursor = conn.cursor()
    
    # Tabla eventos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS eventos_ufc (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            fecha TEXT,
            cartelera TEXT,
            ultima_actualizacion TEXT
        )
    ''')
    
    # Tabla peleadores
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
            odds TEXT,
            ultima_actualizacion TEXT
        )
    ''')
    conn.commit()
    return conn


def insertar_peleadores_base():
    """Inserta peleadores base para que nunca falten datos"""
    conn = sqlite3.connect("data/betting_stats.db")
    cursor = conn.cursor()
    
    peleadores_base = [
        ("Renato Moicano", "19-5-1", 180, 70, 183, "Striker", 0.65, 0.55, "N/A"),
        ("Grant Duncan", "12-3-0", 185, 77, 188, "Striker", 0.70, 0.45, "N/A"),
        ("Bruna Brasil", "11-6-1", 167, 52, 166, "MMA", 0.90, 0.50, "+390"),
        ("Alexia Thainara", "13-1-0", 162, 52, 170, "MMA", 0.50, 0.50, "-520"),
        ("Israel Adesanya", "24-5-0", 193, 84, 203, "Freestyle", 0.90, 0.50, "-120"),
        ("Joe Pyfer", "15-3-0", 188, 84, 190, "Boxing", 0.60, 0.50, "-106"),
        ("Maycee Barber", "15-2-0", 165, 57, 165, "MMA", 0.90, 0.50, "-148"),
        ("Alexa Grasso", "16-5-1", 165, 57, 167, "MMA", 0.50, 0.60, "+124"),
    ]
    
    for p in peleadores_base:
        cursor.execute('''
            INSERT OR IGNORE INTO peleadores_ufc 
            (nombre, record, altura, peso, alcance, postura, ko_rate, grappling, odds, ultima_actualizacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*p, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    print(f"✅ {len(peleadores_base)} peleadores base insertados")


def ejecutar_actualizacion():
    """Ejecuta todo el proceso de actualización"""
    print("="*50)
    print("🔄 ACTUALIZANDO DATOS UFC")
    print("="*50)
    
    # Inicializar BD
    inicializar_bd()
    
    # Insertar peleadores base (siempre)
    insertar_peleadores_base()
    
    # Intentar extraer cartelera real
    nombre, peleas = extraer_cartelera_actual()
    
    # Si falla, usar fallback
    if not peleas:
        print("⚠️ Scraper falló, usando fallback...")
        nombre, peleas = extraer_cartelera_fallback()
    
    if nombre and peleas:
        conn = sqlite3.connect("data/betting_stats.db")
        cursor = conn.cursor()
        
        # Limpiar eventos viejos
        cursor.execute("DELETE FROM eventos_ufc")
        
        # Insertar nuevo evento
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        cursor.execute('''
            INSERT INTO eventos_ufc (nombre, fecha, cartelera, ultima_actualizacion)
            VALUES (?, ?, ?, ?)
        ''', (nombre, fecha_hoy, json.dumps(peleas, ensure_ascii=False), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ ACTUALIZACIÓN COMPLETADA")
        print(f"📅 Evento: {nombre}")
        print(f"🥊 Peleas cargadas: {len(peleas)}")
        
        # Mostrar primeras peleas
        for i, pelea in enumerate(peleas[:5], 1):
            print(f"   {i}. {pelea['peleador1']} vs {pelea['peleador2']}")
    else:
        print("❌ No se pudo actualizar la cartelera")

if __name__ == "__main__":
    ejecutar_actualizacion()
    
    conn.close()

if __name__ == "__main__":
    ejecutar_actualizacion()
