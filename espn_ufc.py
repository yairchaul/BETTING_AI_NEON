# -*- coding: utf-8 -*-
"""
ESPN UFC - Scraper 100% DINÁMICO
Obtiene la cartelera real desde ESPN sin datos fijos
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
        """Obtiene la cartelera real desde ESPN de forma dinámica"""
        logger.info("🔍 Buscando cartelera UFC actual (100% dinámico)...")
        
        # Método 1: Buscar evento activo desde la página principal
        evento_url = self._encontrar_evento_activo()
        
        if evento_url:
            combates = self._scrapear_evento(evento_url)
            if combates and len(combates) >= 2:
                logger.info(f"✅ Cartelera real obtenida: {len(combates)} combates")
                self._guardar_en_bd(combates)
                return combates
        
        # Método 2: Buscar en la API de ESPN
        combates = self._scrapear_api_espn()
        if combates and len(combates) >= 2:
            logger.info(f"✅ Cartelera desde API ESPN: {len(combates)} combates")
            self._guardar_en_bd(combates)
            return combates
        
        # Método 3: Buscar en UFC.com
        combates = self._scrapear_ufc_com()
        if combates and len(combates) >= 2:
            logger.info(f"✅ Cartelera desde UFC.com: {len(combates)} combates")
            self._guardar_en_bd(combates)
            return combates
        
        # Fallback: última cartelera guardada (máximo 7 días)
        logger.warning("⚠️ No se pudo obtener cartelera real. Buscando en BD...")
        combates = self._obtener_ultima_cartelera_bd()
        
        if combates:
            # Verificar si la cartelera es reciente (menos de 7 días)
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT ultima_actualizacion FROM eventos_ufc ORDER BY id DESC LIMIT 1")
                row = cursor.fetchone()
                conn.close()
                if row:
                    fecha_guardado = datetime.fromisoformat(row[0])
                    if (datetime.now() - fecha_guardado).days <= 7:
                        return combates
            except:
                pass
        
        logger.warning("❌ No hay cartelera reciente disponible")
        return []

    def _encontrar_evento_activo(self):
        """Busca el evento activo en la página principal de ESPN"""
        urls = [
            "https://www.espn.com.mx/mma/",
            "https://www.espn.com/mma/",
            "https://www.espn.com/mma/schedule",
        ]
        
        for url in urls:
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Buscar enlaces a fightcenter
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if '/mma/fightcenter/_/id/' in href:
                        # Extraer ID del evento
                        match = re.search(r'/id/(\d+)', href)
                        if match:
                            event_id = match.group(1)
                            return f"https://www.espn.com.mx/mma/fightcenter/_/id/{event_id}/liga/ufc"
            except Exception as e:
                logger.debug(f"Error buscando evento en {url}: {e}")
                continue
        
        return None

    def _scrapear_evento(self, url):
        """Scrapea un evento específico de ESPN"""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            combates = []
            
            # Extraer nombre del evento
            nombre_evento = "UFC Fight Night"
            titulo = soup.select_one('.headline h1, .event-title, h1')
            if titulo:
                nombre_evento = titulo.get_text(strip=True)
                nombre_evento = re.sub(r'Cobertura.*$', '', nombre_evento).strip()
            
            # Extraer fecha
            fecha_evento = self._extraer_fecha(soup)
            
            # Buscar peleas con múltiples selectores
            selectores = [
                '.fight-card', '.matchupCard', '.main-card .fight', 
                '.prelims .fight', '.competitors', '.fight-card__fight'
            ]
            
            peleas = []
            for selector in selectores:
                peleas.extend(soup.select(selector))
            
            # Eliminar duplicados
            peleas = list(dict.fromkeys(peleas))
            
            for pelea in peleas[:15]:
                try:
                    # Extraer nombres
                    p1_nombre = None
                    p2_nombre = None
                    
                    # Selector 1: .fighter-name
                    fighters = pelea.select('.fighter-name')
                    if len(fighters) >= 2:
                        p1_nombre = fighters[0].get_text(strip=True)
                        p2_nombre = fighters[1].get_text(strip=True)
                    
                    # Selector 2: .competitor__name
                    if not p1_nombre:
                        comps = pelea.select('.competitor__name')
                        if len(comps) >= 2:
                            p1_nombre = comps[0].get_text(strip=True)
                            p2_nombre = comps[1].get_text(strip=True)
                    
                    # Selector 3: texto con "vs"
                    if not p1_nombre:
                        texto = pelea.get_text()
                        if 'vs' in texto.lower():
                            partes = texto.lower().split('vs')
                            if len(partes) >= 2:
                                p1_nombre = partes[0].strip()
                                p2_nombre = partes[1].strip()
                                p1_nombre = re.sub(r'[^\w\sáéíóúñÑ\.\-]', '', p1_nombre)
                                p2_nombre = re.sub(r'[^\w\sáéíóúñÑ\.\-]', '', p2_nombre)
                    
                    if p1_nombre and p2_nombre:
                        p1_nombre = self._limpiar_nombre(p1_nombre)
                        p2_nombre = self._limpiar_nombre(p2_nombre)
                        
                        # Extraer categoría
                        categoria = "Peso Pactado"
                        cat_elem = pelea.select_one('.weight-class, .category, .group-name')
                        if cat_elem:
                            categoria = cat_elem.get_text(strip=True)
                        
                        combates.append({
                            'peleador1': {'nombre': p1_nombre},
                            'peleador2': {'nombre': p2_nombre},
                            'categoria': categoria,
                            'evento': nombre_evento,
                            'fecha_evento': fecha_evento,
                            'url_fuente': url
                        })
                        
                except Exception as e:
                    logger.debug(f"Error parseando pelea: {e}")
                    continue
            
            return combates
            
        except Exception as e:
            logger.error(f"Error scrapeando evento {url}: {e}")
            return []

    def _scrapear_api_espn(self):
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
                    fecha_evento = event.get('date', '')[:10]
                    
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
                                    'fecha_evento': fecha_evento
                                })
                
                if combates:
                    return combates
                    
        except Exception as e:
            logger.debug(f"Error en API ESPN: {e}")
        
        return None

    def _scrapear_ufc_com(self):
        """Scrapea UFC.com como alternativa"""
        try:
            url = "https://www.ufc.com/events"
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            combates = []
            
            # Buscar eventos
            eventos = soup.select('.c-card-event, .event-card')
            
            for evento in eventos[:1]:  # Solo el próximo evento
                nombre_evento = "UFC Event"
                titulo = evento.select_one('h3, .headline')
                if titulo:
                    nombre_evento = titulo.get_text(strip=True)
                
                # Buscar peleas
                peleas = evento.select('.c-listing-fight, .fight-row')
                
                for pelea in peleas[:10]:
                    try:
                        fighters = pelea.select('.fighter-name, .name')
                        if len(fighters) >= 2:
                            p1 = fighters[0].get_text(strip=True)
                            p2 = fighters[1].get_text(strip=True)
                            if p1 and p2:
                                combates.append({
                                    'peleador1': {'nombre': p1},
                                    'peleador2': {'nombre': p2},
                                    'categoria': 'Peso Pactado',
                                    'evento': nombre_evento,
                                    'fecha_evento': None
                                })
                    except:
                        continue
                
                if combates:
                    return combates
                    
        except Exception as e:
            logger.debug(f"Error en UFC.com: {e}")
        
        return None

    def _extraer_fecha(self, soup):
        """Extrae la fecha del evento"""
        try:
            # Buscar en metadatos
            meta = soup.select_one('meta[property="article:published_time"]')
            if meta:
                return meta.get('content', '')[:10]
            
            # Buscar en texto
            texto = soup.get_text()
            patrones = [
                r'(\d{1,2}\s+de\s+[A-Za-zéúíóá]+\s+de\s+\d{4})',
                r'(\d{1,2}/\d{1,2}/\d{4})',
                r'(\d{4}-\d{2}-\d{2})',
            ]
            for patron in patrones:
                match = re.search(patron, texto)
                if match:
                    return match.group(1)
        except:
            pass
        return datetime.now().strftime("%Y-%m-%d")

    def _limpiar_nombre(self, nombre):
        """Limpia el nombre del peleador"""
        nombre = re.sub(r'\([^)]*\)', '', nombre)
        nombre = re.sub(r'[^\w\sáéíóúñÑ\.\-]', '', nombre)
        nombre = re.sub(r'#\d+', '', nombre)
        nombre = re.sub(r'vs\.?\s*', '', nombre, flags=re.IGNORECASE)
        nombre = ' '.join(nombre.split())
        return nombre.strip()

    def _obtener_ultima_cartelera_bd(self):
        """Recupera la última cartelera guardada"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT cartelera, ultima_actualizacion FROM eventos_ufc ORDER BY id DESC LIMIT 1")
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
                "UFC Actual",
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
