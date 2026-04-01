# -*- coding: utf-8 -*-
"""
ESPN UFC - Scraper Definitivo con ESPN FightCenter
100% DINÁMICO - Obtiene la cartelera real desde ESPN
Fuente: https://www.espn.com.mx/mma/fightcenter/
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
            'Accept-Language': 'es-ES,es;q=0.8,en;q=0.5',
        }
        self._crear_tablas()
        self.eventos_cache = []

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
                    fecha_evento TEXT,
                    url_espn TEXT
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
        """Obtiene la cartelera actual desde ESPN FightCenter"""
        logger.info("🔍 Obteniendo cartelera UFC desde ESPN FightCenter...")
        
        # Intentar scraping desde ESPN
        combates = self._scrape_espn_fightcenter()
        
        if combates and len(combates) >= 2:
            logger.info(f"✅ Cartelera ESPN obtenida: {len(combates)} combates")
            self._guardar_en_bd(combates)
            self.eventos_cache = combates
            return combates
        
        # Fallback: intentar con la API de ESPN
        logger.info("🔄 Intentando con API de ESPN...")
        combates = self._scrape_espn_api()
        
        if combates:
            logger.info(f"✅ Cartelera API obtenida: {len(combates)} combates")
            self._guardar_en_bd(combates)
            self.eventos_cache = combates
            return combates
        
        # Último recurso: recuperar de BD
        logger.info("📀 Recuperando última cartelera guardada...")
        combates = self._obtener_ultima_cartelera_bd()
        
        if combates:
            return combates
        
        logger.warning("❌ No se pudo obtener cartelera")
        return []

    def _scrape_espn_fightcenter(self):
        """Scrapea el FightCenter de ESPN para UFC"""
        # Buscar eventos activos de UFC
        urls = [
            "https://www.espn.com.mx/mma/fightcenter/_/id/600058693/liga/ufc",  # Evento actual
            "https://www.espn.com/mma/fightcenter",  # General
        ]
        
        for url in urls:
            try:
                response = requests.get(url, headers=self.headers, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                combates = []
                
                # Buscar nombre del evento
                nombre_evento = "UFC Fight Night"
                titulo = soup.select_one('.headline h1, .event-title, .SectionHeader__title')
                if titulo:
                    nombre_evento = titulo.get_text(strip=True)
                
                # Buscar fecha
                fecha_evento = self._extraer_fecha_espn(soup)
                
                # Buscar todas las peleas
                peleas = soup.select('.fight-card, .matchupCard, .competitors')
                
                if not peleas:
                    # Selector alternativo para tarjeta principal
                    peleas = soup.select('.main-card .fight, .prelims .fight')
                
                for pelea in peleas:
                    try:
                        # Extraer nombres
                        nombres = pelea.select('.fighter-name, .competitor__name, .name')
                        if len(nombres) >= 2:
                            p1 = nombres[0].get_text(strip=True)
                            p2 = nombres[1].get_text(strip=True)
                            
                            # Limpiar nombres
                            p1 = self._limpiar_nombre(p1)
                            p2 = self._limpiar_nombre(p2)
                            
                            if p1 and p2 and len(p1) > 2 and len(p2) > 2:
                                # Extraer categoría
                                categoria = self._extraer_categoria_espn(pelea, soup)
                                
                                # Extraer récords si están disponibles
                                record1 = self._extraer_record(pelea, 0)
                                record2 = self._extraer_record(pelea, 1)
                                
                                # Extraer estadísticas adicionales
                                stats = self._extraer_estadisticas(pelea)
                                
                                combates.append({
                                    'peleador1': {
                                        'nombre': p1,
                                        'record': record1,
                                        **stats.get('p1', {})
                                    },
                                    'peleador2': {
                                        'nombre': p2,
                                        'record': record2,
                                        **stats.get('p2', {})
                                    },
                                    'categoria': categoria,
                                    'evento': nombre_evento,
                                    'fecha_evento': fecha_evento,
                                    'url_fuente': url
                                })
                    except Exception as e:
                        logger.debug(f"Error parseando pelea: {e}")
                        continue
                
                if combates:
                    logger.info(f"Encontradas {len(combates)} peleas en {url}")
                    return combates
                    
            except Exception as e:
                logger.warning(f"Error en {url}: {e}")
                continue
        
        return None

    def _scrape_espn_api(self):
        """Intenta obtener datos desde la API interna de ESPN"""
        try:
            # API de ESPN para UFC
            api_url = "https://site.api.espn.com/apis/site/v2/sports/mma/ufc/scoreboard"
            response = requests.get(api_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                combates = []
                
                events = data.get('events', [])
                for event in events:
                    nombre_evento = event.get('name', 'UFC Event')
                    fecha_evento = event.get('date', '')
                    
                    competitions = event.get('competitions', [])
                    for comp in competitions:
                        competitors = comp.get('competitors', [])
                        if len(competitors) >= 2:
                            p1 = competitors[0].get('athlete', {}).get('displayName', '')
                            p2 = competitors[1].get('athlete', {}).get('displayName', '')
                            
                            if p1 and p2:
                                combates.append({
                                    'peleador1': {'nombre': p1},
                                    'peleador2': {'nombre': p2},
                                    'categoria': comp.get('group', {}).get('name', 'Peso Pactado'),
                                    'evento': nombre_evento,
                                    'fecha_evento': fecha_evento[:10] if fecha_evento else None
                                })
                
                if combates:
                    return combates
                    
        except Exception as e:
            logger.warning(f"Error en API ESPN: {e}")
        
        return None

    def _extraer_fecha_espn(self, soup):
        """Extrae la fecha del evento desde el HTML de ESPN"""
        try:
            # Buscar en metadatos
            meta_date = soup.select_one('meta[property="article:published_time"]')
            if meta_date:
                return meta_date.get('content', '')[:10]
            
            # Buscar en texto
            texto = soup.get_text()
            patrones = [
                r'(\d{1,2}\s+de\s+[A-Za-zéúíóá]+\s+de\s+\d{4})',
                r'(\d{1,2}/\d{1,2}/\d{4})',
            ]
            for patron in patrones:
                match = re.search(patron, texto)
                if match:
                    return match.group(1)
        except:
            pass
        return datetime.now().strftime("%Y-%m-%d")

    def _extraer_categoria_espn(self, pelea, soup):
        """Extrae la categoría/peso de la pelea"""
        try:
            # Buscar en el elemento de la pelea
            cat_elem = pelea.select_one('.weight-class, .category, .group-name')
            if cat_elem:
                return cat_elem.get_text(strip=True)
            
            # Buscar en el contexto
            texto = pelea.get_text()
            categorias = ['Peso Pesado', 'Peso Semipesado', 'Peso Medio', 
                         'Peso Welter', 'Peso Ligero', 'Peso Pluma', 
                         'Peso Gallo', 'Peso Mosca', 'Peso Paja',
                         'Heavyweight', 'Light Heavyweight', 'Middleweight',
                         'Welterweight', 'Lightweight', 'Featherweight',
                         'Bantamweight', 'Flyweight', 'Strawweight']
            
            for cat in categorias:
                if cat.lower() in texto.lower():
                    return cat
        except:
            pass
        return 'Peso Pactado'

    def _extraer_record(self, pelea, idx):
        """Extrae el récord del peleador"""
        try:
            records = pelea.select('.record, .record-text, .fighter-record')
            if idx < len(records):
                return records[idx].get_text(strip=True)
        except:
            pass
        return None

    def _extraer_estadisticas(self, pelea):
        """Extrae estadísticas adicionales (altura, alcance, etc.)"""
        stats = {'p1': {}, 'p2': {}}
        try:
            # Buscar tablas de estadísticas
            stat_rows = pelea.select('.stat-row, .fighter-stats')
            for row in stat_rows:
                texto = row.get_text().lower()
                valores = row.select('.value, .stat-value')
                if len(valores) >= 2:
                    if 'altura' in texto or 'height' in texto:
                        stats['p1']['altura'] = valores[0].get_text(strip=True)
                        stats['p2']['altura'] = valores[1].get_text(strip=True)
                    elif 'alcance' in texto or 'reach' in texto:
                        stats['p1']['alcance'] = valores[0].get_text(strip=True)
                        stats['p2']['alcance'] = valores[1].get_text(strip=True)
        except:
            pass
        return stats

    def _limpiar_nombre(self, nombre):
        """Limpia el nombre del peleador"""
        # Eliminar texto entre paréntesis
        nombre = re.sub(r'\([^)]*\)', '', nombre)
        # Eliminar emojis y caracteres especiales
        nombre = re.sub(r'[^\w\sáéíóúñÑ]', '', nombre)
        # Eliminar números de ranking
        nombre = re.sub(r'#\d+', '', nombre)
        # Eliminar espacios extra
        nombre = ' '.join(nombre.split())
        return nombre.strip()

    def _obtener_ultima_cartelera_bd(self):
        """Recupera la última cartelera guardada"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT cartelera FROM eventos_ufc ORDER BY ultima_actualizacion DESC LIMIT 1")
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
            
            fecha_evento = combates[0].get('fecha_evento') if combates else None
            
            cursor.execute('''
                INSERT INTO eventos_ufc (nombre, fecha, cartelera, ultima_actualizacion, fecha_evento)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                "UFC ESPN",
                datetime.now().strftime("%Y-%m-%d"),
                json.dumps(combates, ensure_ascii=False),
                datetime.now().isoformat(),
                fecha_evento
            ))
            
            conn.commit()
            logger.info(f"✅ {len(combates)} combates guardados en BD")
        except Exception as e:
            logger.error(f"Error guardando: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
