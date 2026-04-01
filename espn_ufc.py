# -*- coding: utf-8 -*-
"""
ESPN UFC - Scraper que usa API interna de ESPN (más estable que scraping)
"""

import requests
import json
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ESPN_UFC:
    def __init__(self):
        self.db_path = 'data/betting_stats.db'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
        }
        self._crear_tablas()

    def _crear_tablas(self):
        """Crea las tablas necesarias"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS eventos_ufc (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT,
                    fecha TEXT,
                    cartelera TEXT,
                    ultima_actualizacion TEXT,
                    fecha_evento TEXT
                )
            ''')
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
            conn.close()
        except Exception as e:
            logger.error(f"Error creando tablas: {e}")

    def get_events(self):
        """Obtiene la cartelera desde la API de ESPN"""
        logger.info("🔍 Obteniendo cartelera UFC desde API ESPN...")
        
        # API de ESPN para MMA
        api_url = "https://site.api.espn.com/apis/site/v2/sports/mma/ufc/scoreboard"
        
        try:
            response = requests.get(api_url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                combates = []
                
                events = data.get('events', [])
                for event in events:
                    nombre_evento = event.get('name', 'UFC Event')
                    fecha_evento = event.get('date', '')
                    if fecha_evento:
                        fecha_evento = fecha_evento[:10]
                    
                    competitions = event.get('competitions', [])
                    for comp in competitions:
                        competitors = comp.get('competitors', [])
                        if len(competitors) >= 2:
                            # Extraer nombres
                            p1_data = competitors[0].get('athlete', {})
                            p2_data = competitors[1].get('athlete', {})
                            
                            p1_nombre = p1_data.get('displayName', '')
                            p2_nombre = p2_data.get('displayName', '')
                            
                            # Extraer récords si están disponibles
                            p1_record = p1_data.get('record', {}).get('displayValue', 'N/A')
                            p2_record = p2_data.get('record', {}).get('displayValue', 'N/A')
                            
                            if p1_nombre and p2_nombre:
                                combates.append({
                                    'peleador1': {
                                        'nombre': p1_nombre,
                                        'record': p1_record
                                    },
                                    'peleador2': {
                                        'nombre': p2_nombre,
                                        'record': p2_record
                                    },
                                    'categoria': comp.get('group', {}).get('name', 'Peso Pactado'),
                                    'evento': nombre_evento,
                                    'fecha_evento': fecha_evento
                                })
                
                if combates:
                    logger.info(f"✅ {len(combates)} combates obtenidos de API ESPN")
                    self._guardar_en_bd(combates)
                    return combates
                else:
                    logger.warning("No se encontraron combates en la API")
            else:
                logger.warning(f"Error en API: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error en API ESPN: {e}")
        
        # Fallback: intentar con la página web
        logger.info("🔄 Intentando scraping web como fallback...")
        combates = self._scrapear_web_fallback()
        if combates:
            self._guardar_en_bd(combates)
            return combates
        
        # Último recurso: cartelera de BD
        logger.info("📀 Recuperando última cartelera guardada...")
        return self._obtener_ultima_cartelera_bd()

    def _scrapear_web_fallback(self):
        """Scraping web como fallback"""
        try:
            from bs4 import BeautifulSoup
            url = "https://www.espn.com/mma/schedule"
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            combates = []
            filas = soup.select('.Table__TR')
            
            for fila in filas[:15]:
                texto = fila.get_text()
                if 'vs' in texto.lower():
                    partes = texto.lower().split('vs')
                    if len(partes) >= 2:
                        p1 = partes[0].strip()
                        p2 = partes[1].strip()
                        # Limpiar nombres
                        p1 = p1.split('\n')[-1].strip()
                        p2 = p2.split('\n')[0].strip()
                        if p1 and p2 and len(p1) > 2 and len(p2) > 2:
                            combates.append({
                                'peleador1': {'nombre': p1},
                                'peleador2': {'nombre': p2},
                                'categoria': 'Peso Pactado',
                                'evento': 'UFC Fight Night',
                                'fecha_evento': None
                            })
            return combates
        except Exception as e:
            logger.error(f"Error en fallback web: {e}")
            return []

    def _obtener_ultima_cartelera_bd(self):
        """Recupera la última cartelera guardada"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT cartelera FROM eventos_ufc ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            if row and row[0]:
                return json.loads(row[0])
        except:
            pass
        return []

    def _guardar_en_bd(self, combates):
        """Guarda la cartelera en BD"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM eventos_ufc")
            cursor.execute('''
                INSERT INTO eventos_ufc (nombre, fecha, cartelera, ultima_actualizacion)
                VALUES (?, ?, ?, ?)
            ''', ("UFC API", datetime.now().strftime("%Y-%m-%d"), json.dumps(combates), datetime.now().isoformat()))
            conn.commit()
        except Exception as e:
            logger.error(f"Error guardando: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
