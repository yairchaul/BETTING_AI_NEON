# -*- coding: utf-8 -*-
"""
ESPN UFC - Scraper que obtiene cartelera Y datos de peleadores
"""

import requests
import json
import sqlite3
import logging
import re
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
        """Obtiene la cartelera y datos de peleadores"""
        logger.info("🔍 Obteniendo cartelera UFC...")
        
        combates = self._obtener_desde_api_espn()
        
        if combates:
            logger.info(f"✅ {len(combates)} combates obtenidos")
            self._guardar_en_bd(combates)
            return combates
        
        # Fallback a BD
        return self._obtener_ultima_cartelera_bd()

    def _obtener_desde_api_espn(self):
        """Obtiene datos desde la API de ESPN"""
        try:
            url = "https://site.api.espn.com/apis/site/v2/sports/mma/ufc/scoreboard"
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            combates = []
            
            for event in data.get('events', []):
                nombre_evento = event.get('name', 'UFC Event')
                fecha_evento = event.get('date', '')[:10]
                
                for comp in event.get('competitions', []):
                    competitors = comp.get('competitors', [])
                    if len(competitors) >= 2:
                        p1_data = competitors[0].get('athlete', {})
                        p2_data = competitors[1].get('athlete', {})
                        
                        p1_nombre = p1_data.get('displayName', '')
                        p2_nombre = p2_data.get('displayName', '')
                        
                        if p1_nombre and p2_nombre:
                            # Obtener y guardar datos de cada peleador
                            p1_detalle = self._obtener_detalle_peleador(p1_nombre)
                            p2_detalle = self._obtener_detalle_peleador(p2_nombre)
                            
                            combates.append({
                                'peleador1': p1_detalle,
                                'peleador2': p2_detalle,
                                'categoria': comp.get('group', {}).get('name', 'Peso Pactado'),
                                'evento': nombre_evento,
                                'fecha_evento': fecha_evento
                            })
            
            return combates
        except Exception as e:
            logger.error(f"Error en API: {e}")
            return []

    def _obtener_detalle_peleador(self, nombre):
        """Obtiene detalles completos de un peleador"""
        # Primero buscar en BD
        datos = self._buscar_en_bd(nombre)
        if datos:
            return datos
        
        # Si no está en BD, buscar en internet
        datos = self._buscar_en_internet(nombre)
        if datos:
            self._guardar_peleador_en_bd(datos)
            return datos
        
        # Fallback con datos mínimos
        return {'nombre': nombre, 'record': 'N/A', 'altura': 0, 'alcance': 0, 'ko_rate': 0.5, 'grappling': 0.5, 'odds': 'N/A'}

    def _buscar_en_bd(self, nombre):
        """Busca peleador en BD"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT nombre, record, altura, alcance, ko_rate, odds
                FROM peleadores_ufc 
                WHERE nombre = ? OR nombre LIKE ?
                LIMIT 1
            ''', (nombre, f"%{nombre}%"))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'nombre': row[0],
                    'record': row[1] if row[1] else 'N/A',
                    'altura': int(row[2]) if row[2] else 0,
                    'alcance': int(row[3]) if row[3] else 0,
                    'ko_rate': float(row[4]) if row[4] else 0.5,
                    'grappling': 0.5,
                    'odds': row[5] if row[5] else 'N/A'
                }
        except:
            pass
        return None

    def _buscar_en_internet(self, nombre):
        """Busca datos del peleador en internet (API de ESPN)"""
        try:
            # Buscar en ESPN
            search_url = f"https://site.api.espn.com/apis/site/v2/sports/mma/ufc/athletes?search={nombre.replace(' ', '%20')}"
            response = requests.get(search_url, headers=self.headers, timeout=8)
            
            if response.status_code == 200:
                data = response.json()
                athletes = data.get('athletes', [])
                if athletes:
                    athlete = athletes[0]
                    stats = athlete.get('stats', [])
                    
                    altura = 0
                    alcance = 0
                    ko_rate = 0.5
                    
                    for stat in stats:
                        stat_name = stat.get('name', '')
                        if stat_name == 'height':
                            altura = self._convertir_altura(stat.get('displayValue', ''))
                        elif stat_name == 'reach':
                            alcance = self._convertir_alcance(stat.get('displayValue', ''))
                        elif stat_name == 'knockoutPercentage':
                            try:
                                ko_rate = float(stat.get('value', 0.5))
                            except:
                                ko_rate = 0.5
                    
                    return {
                        'nombre': athlete.get('displayName', nombre),
                        'record': athlete.get('record', {}).get('displayValue', 'N/A'),
                        'altura': altura,
                        'alcance': alcance,
                        'ko_rate': ko_rate,
                        'grappling': 0.5,
                        'odds': 'N/A'
                    }
        except Exception as e:
            logger.debug(f"Error buscando {nombre}: {e}")
        
        return None

    def _convertir_altura(self, altura_str):
        """Convierte altura a cm"""
        if not altura_str:
            return 0
        try:
            match = re.search(r"(\d+)'?\s*(\d+)?", altura_str)
            if match:
                pies = int(match.group(1))
                pulgadas = int(match.group(2)) if match.group(2) else 0
                return int(pies * 30.48 + pulgadas * 2.54)
        except:
            pass
        return 0

    def _convertir_alcance(self, alcance_str):
        """Convierte alcance a cm"""
        if not alcance_str:
            return 0
        try:
            match = re.search(r"(\d+)", alcance_str)
            if match:
                return int(int(match.group(1)) * 2.54)
        except:
            pass
        return 0

    def _guardar_peleador_en_bd(self, datos):
        """Guarda peleador en BD"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO peleadores_ufc 
                (nombre, record, altura, alcance, ko_rate, odds, ultima_actualizacion)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                datos['nombre'],
                datos['record'],
                datos['altura'],
                datos['alcance'],
                datos['ko_rate'],
                datos.get('odds', 'N/A'),
                datetime.now().isoformat()
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.debug(f"Error guardando {datos['nombre']}: {e}")

    def _guardar_en_bd(self, combates):
        """Guarda la cartelera en BD"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM eventos_ufc")
            
            fecha_evento = combates[0].get('fecha_evento') if combates else None
            
            cursor.execute('''
                INSERT INTO eventos_ufc (nombre, fecha, cartelera, ultima_actualizacion, fecha_evento)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                "UFC Actual",
                datetime.now().strftime("%Y-%m-%d"),
                json.dumps(combates, ensure_ascii=False),
                datetime.now().isoformat(),
                fecha_evento
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error guardando: {e}")

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
