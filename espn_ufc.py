# -*- coding: utf-8 -*-
"""
ESPN UFC - Scraper que funciona igual en local y en la nube
Extrae datos reales desde ESPN y UFC.com sin depender de archivos locales
"""

import requests
from bs4 import BeautifulSoup
import json
import sqlite3
import logging
import re
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class ESPN_UFC:
    def __init__(self):
        self.db_path = 'data/betting_stats.db'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
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
        """Obtiene la cartelera real desde internet (ESPN + UFC.com)"""
        logger.info("🔍 Scrapeando cartelera UFC en tiempo real...")
        
        # MÉTODO 1: API de ESPN (más confiable)
        combates = self._scrapear_api_espn()
        if combates and len(combates) >= 2:
            logger.info(f"✅ {len(combates)} combates desde API ESPN")
            self._guardar_en_bd(combates)
            return combates
        
        # MÉTODO 2: Scraping ESPN.com
        combates = self._scrapear_espn_com()
        if combates and len(combates) >= 2:
            logger.info(f"✅ {len(combates)} combates desde ESPN.com")
            self._guardar_en_bd(combates)
            return combates
        
        # MÉTODO 3: Scraping UFC.com
        combates = self._scrapear_ufc_com()
        if combates and len(combates) >= 2:
            logger.info(f"✅ {len(combates)} combates desde UFC.com")
            self._guardar_en_bd(combates)
            return combates
        
        # Si todo falla, recuperar de BD (última cartelera)
        logger.warning("⚠️ No se pudo obtener cartelera nueva. Usando última guardada.")
        return self._obtener_ultima_cartelera_bd()

    def _scrapear_api_espn(self):
        """Obtiene datos desde la API de ESPN"""
        try:
            # API de eventos UFC
            url = "https://site.api.espn.com/apis/site/v2/sports/mma/ufc/scoreboard"
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
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
                                # Extraer datos detallados del peleador
                                p1_detalle = self._extraer_datos_peleador_api(p1_data)
                                p2_detalle = self._extraer_datos_peleador_api(p2_data)
                                
                                # Guardar en BD
                                self._guardar_peleador_en_bd(p1_nombre, p1_detalle)
                                self._guardar_peleador_en_bd(p2_nombre, p2_detalle)
                                
                                combates.append({
                                    'peleador1': p1_detalle,
                                    'peleador2': p2_detalle,
                                    'categoria': comp.get('group', {}).get('name', 'Peso Pactado'),
                                    'evento': nombre_evento,
                                    'fecha_evento': fecha_evento
                                })
                
                return combates
        except Exception as e:
            logger.error(f"Error en API ESPN: {e}")
        return []

    def _scrapear_espn_com(self):
        """Scrapea la página de ESPN como fallback"""
        try:
            # Buscar evento actual
            url = "https://www.espn.com/mma/schedule"
            response = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            combates = []
            rows = soup.select('.Table__TR')
            
            for row in rows:
                texto = row.get_text()
                if 'vs' in texto.lower():
                    partes = texto.lower().split('vs')
                    if len(partes) >= 2:
                        p1 = partes[0].strip().split('\n')[-1].strip()
                        p2 = partes[1].strip().split('\n')[0].strip()
                        if p1 and p2 and len(p1) > 2 and len(p2) > 2:
                            # Buscar datos adicionales
                            p1_detalle = self._buscar_datos_peleador_web(p1)
                            p2_detalle = self._buscar_datos_peleador_web(p2)
                            
                            self._guardar_peleador_en_bd(p1, p1_detalle)
                            self._guardar_peleador_en_bd(p2, p2_detalle)
                            
                            combates.append({
                                'peleador1': p1_detalle,
                                'peleador2': p2_detalle,
                                'categoria': 'Peso Pactado',
                                'evento': 'UFC Fight Night',
                                'fecha_evento': None
                            })
            
            return combates[:10]
        except Exception as e:
            logger.error(f"Error en ESPN.com: {e}")
        return []

    def _scrapear_ufc_com(self):
        """Scrapea UFC.com como último recurso"""
        try:
            url = "https://www.ufc.com/events"
            response = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            combates = []
            cards = soup.select('.c-card-event')
            
            for card in cards[:1]:  # Solo el próximo evento
                peleas = card.select('.c-listing-fight')
                for pelea in peleas[:10]:
                    try:
                        fighters = pelea.select('.fighter-name')
                        if len(fighters) >= 2:
                            p1 = fighters[0].get_text(strip=True)
                            p2 = fighters[1].get_text(strip=True)
                            
                            p1_detalle = {'nombre': p1, 'record': 'N/A', 'ko_rate': 0.5}
                            p2_detalle = {'nombre': p2, 'record': 'N/A', 'ko_rate': 0.5}
                            
                            self._guardar_peleador_en_bd(p1, p1_detalle)
                            self._guardar_peleador_en_bd(p2, p2_detalle)
                            
                            combates.append({
                                'peleador1': p1_detalle,
                                'peleador2': p2_detalle,
                                'categoria': 'Peso Pactado',
                                'evento': 'UFC Event',
                                'fecha_evento': None
                            })
                    except:
                        continue
            return combates
        except Exception as e:
            logger.error(f"Error en UFC.com: {e}")
        return []

    def _extraer_datos_peleador_api(self, athlete_data):
        """Extrae datos detallados del peleador desde la API"""
        nombre = athlete_data.get('displayName', '')
        record = athlete_data.get('record', {}).get('displayValue', 'N/A')
        
        # Extraer estadísticas
        altura = 0
        alcance = 0
        ko_rate = 0.5
        odds = 'N/A'
        
        stats = athlete_data.get('stats', [])
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
            'nombre': nombre,
            'record': record,
            'altura': altura,
            'alcance': alcance,
            'ko_rate': ko_rate,
            'grappling': 0.5,
            'odds': odds
        }

    def _buscar_datos_peleador_web(self, nombre):
        """Busca datos del peleador en la web"""
        try:
            # Buscar en ESPN
            search_url = f"https://site.api.espn.com/apis/site/v2/sports/mma/ufc/athletes?search={nombre.replace(' ', '%20')}"
            response = requests.get(search_url, headers=self.headers, timeout=8)
            if response.status_code == 200:
                data = response.json()
                athletes = data.get('athletes', [])
                if athletes:
                    return self._extraer_datos_peleador_api(athletes[0])
        except:
            pass
        
        return {'nombre': nombre, 'record': 'N/A', 'ko_rate': 0.5, 'grappling': 0.5, 'odds': 'N/A'}

    def _convertir_altura(self, altura_str):
        """Convierte altura de formato '6' 2"' a cm"""
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
        """Convierte alcance de formato '74"' a cm"""
        if not alcance_str:
            return 0
        try:
            match = re.search(r"(\d+)", alcance_str)
            if match:
                pulgadas = int(match.group(1))
                return int(pulgadas * 2.54)
        except:
            pass
        return 0

    def _guardar_peleador_en_bd(self, nombre, datos):
        """Guarda o actualiza peleador en BD"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO peleadores_ufc 
                (nombre, record, altura, alcance, ko_rate, grappling, odds, ultima_actualizacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                nombre,
                datos.get('record', 'N/A'),
                datos.get('altura', 0),
                datos.get('alcance', 0),
                datos.get('ko_rate', 0.5),
                datos.get('grappling', 0.5),
                datos.get('odds', 'N/A'),
                datetime.now().isoformat()
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.debug(f"Error guardando {nombre}: {e}")

    def _obtener_datos_peleador_bd(self, nombre):
        """Obtiene datos del peleador desde BD"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT nombre, record, altura, alcance, ko_rate, grappling, odds
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
                    'altura': row[2] if row[2] else 0,
                    'alcance': row[3] if row[3] else 0,
                    'ko_rate': row[4] if row[4] else 0.5,
                    'grappling': row[5] if row[5] else 0.5,
                    'odds': row[6] if row[6] else 'N/A'
                }
            return None
        except:
            return None

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
            logger.info(f"✅ {len(combates)} combates guardados")
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
