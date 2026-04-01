# -*- coding: utf-8 -*-
"""
ESPN UFC - Scraper Completo con Odds y Estadísticas
"""

import requests
from bs4 import BeautifulSoup
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
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

    def _obtener_datos_peleador(self, nombre):
        """Busca los datos del peleador en BD"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT nombre, record, altura, peso, alcance, postura, ko_rate, grappling, odds
                FROM peleadores_ufc 
                WHERE nombre = ? OR nombre LIKE ? 
                LIMIT 1
            ''', (nombre, f'%{nombre}%'))
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    'nombre': row[0],
                    'record': row[1] or '0-0-0',
                    'altura': row[2] if row[2] else 0,
                    'peso': row[3] if row[3] else 0,
                    'alcance': row[4] if row[4] else 0,
                    'postura': row[5] or 'N/A',
                    'ko_rate': row[6] if row[6] else 0.5,
                    'grappling': row[7] if row[7] else 0.5,
                    'odds': row[8] or 'N/A'
                }
            return None
        except:
            return None

    def get_events(self):
        """Obtiene la cartelera con odds desde ESPN"""
        logger.info("🔍 Obteniendo cartelera UFC desde ESPN...")
        
        # URL del evento actual
        url = "https://www.espn.com.mx/mma/fightcenter/_/id/600058693/liga/ufc"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            combates = []
            
            # Extraer nombre del evento
            nombre_evento = "UFC Fight Night: Moicano vs. Duncan"
            titulo = soup.select_one('.headline h1')
            if titulo:
                nombre_evento = titulo.get_text(strip=True)
            
            # Buscar todas las peleas
            peleas = soup.select('.fight-card, .matchupCard')
            
            if not peleas:
                # Selector alternativo
                peleas = soup.select('.main-card .fight, .prelims .fight')
            
            for pelea in peleas:
                try:
                    # Extraer nombres
                    p1_nombre = None
                    p2_nombre = None
                    
                    # Buscar por clase fighter-name
                    fighters = pelea.select('.fighter-name')
                    if len(fighters) >= 2:
                        p1_nombre = fighters[0].get_text(strip=True)
                        p2_nombre = fighters[1].get_text(strip=True)
                    
                    # Si no, buscar en competidores
                    if not p1_nombre:
                        comps = pelea.select('.competitor__name')
                        if len(comps) >= 2:
                            p1_nombre = comps[0].get_text(strip=True)
                            p2_nombre = comps[1].get_text(strip=True)
                    
                    if p1_nombre and p2_nombre:
                        # Limpiar nombres
                        p1_nombre = re.sub(r'\([^)]*\)', '', p1_nombre).strip()
                        p2_nombre = re.sub(r'\([^)]*\)', '', p2_nombre).strip()
                        
                        # Extraer odds si están disponibles
                        odds = pelea.select('.odds, .moneyline')
                        odds_p1 = odds[0].get_text(strip=True) if len(odds) > 0 else None
                        odds_p2 = odds[1].get_text(strip=True) if len(odds) > 1 else None
                        
                        # Extraer categoría
                        categoria = "Peso Pactado"
                        cat_elem = pelea.select_one('.weight-class, .category')
                        if cat_elem:
                            categoria = cat_elem.get_text(strip=True)
                        
                        # Obtener datos de BD
                        datos_p1 = self._obtener_datos_peleador(p1_nombre)
                        datos_p2 = self._obtener_datos_peleador(p2_nombre)
                        
                        # Si hay odds de ESPN, actualizar
                        if odds_p1 and datos_p1:
                            datos_p1['odds'] = odds_p1
                        if odds_p2 and datos_p2:
                            datos_p2['odds'] = odds_p2
                        
                        combates.append({
                            'peleador1': datos_p1 if datos_p1 else {'nombre': p1_nombre},
                            'peleador2': datos_p2 if datos_p2 else {'nombre': p2_nombre},
                            'categoria': categoria,
                            'evento': nombre_evento,
                            'fecha_evento': '2026-04-05'
                        })
                        
                except Exception as e:
                    logger.debug(f"Error en pelea: {e}")
                    continue
            
            if combates:
                logger.info(f"✅ {len(combates)} combates obtenidos")
                self._guardar_en_bd(combates)
                return combates
                
        except Exception as e:
            logger.error(f"Error scraping: {e}")
        
        # Fallback a BD
        return self._obtener_ultima_cartelera_bd()

    def _obtener_ultima_cartelera_bd(self):
        """Recupera última cartelera guardada"""
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
        """Guarda en BD"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM eventos_ufc")
            cursor.execute('''
                INSERT INTO eventos_ufc (nombre, fecha, cartelera, ultima_actualizacion)
                VALUES (?, ?, ?, ?)
            ''', ("UFC ESPN", datetime.now().strftime("%Y-%m-%d"), json.dumps(combates), datetime.now().isoformat()))
            conn.commit()
        except Exception as e:
            logger.error(f"Error guardando: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
