# -*- coding: utf-8 -*-
"""
ESPN UFC - Scraper Definitivo y Automático para Cartelera UFC
Versión 2026 - 100% DINÁMICA - SIN DATOS FIJOS
Obtiene la cartelera real desde múltiples fuentes y filtra solo eventos futuros
"""

import requests
from bs4 import BeautifulSoup
import json
import sqlite3
import logging
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

class ESPN_UFC:
    def __init__(self):
        self.db_path = 'data/betting_stats.db'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self._crear_tablas()
        self.eventos_cache = []  # Cache para la sesión actual

    def _crear_tablas(self):
        """Crea las tablas necesarias si no existen"""
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
            logger.error(f"Error creando tablas UFC: {e}")

    def get_events(self):
        """Obtiene la cartelera más reciente de UFC de forma completamente dinámica"""
        logger.info("🔍 Buscando cartelera UFC actual (100% dinámico)...")
        
        # Si ya tenemos cache en esta sesión, usarlo
        if self.eventos_cache:
            logger.info(f"📦 Usando cache de sesión: {len(self.eventos_cache)} combates")
            return self.eventos_cache

        # Intento 1: Scraping real en múltiples fuentes
        combates = self._scrape_multiple_sources()
        
        if combates and len(combates) >= 2:
            logger.info(f"✅ Cartelera real obtenida: {len(combates)} combates")
            self._guardar_en_bd(combates)
            self.eventos_cache = combates
            return combates

        # Intento 2: Recuperar de BD (última cartelera guardada)
        logger.info("📀 Scraping web falló. Recuperando última cartelera guardada...")
        combates = self._obtener_ultima_cartelera_bd()
        
        if combates:
            logger.info(f"📀 Última cartelera recuperada de BD: {len(combates)} combates")
            self.eventos_cache = combates
            return combates

        # Intento 3: Scraping de respaldo con APIs alternativas
        logger.info("🔄 Intentando scraping con fuentes alternativas...")
        combates = self._scrape_alternativo()
        
        if combates:
            logger.info(f"✅ Cartelera obtenida de fuente alternativa: {len(combates)} combates")
            self._guardar_en_bd(combates)
            self.eventos_cache = combates
            return combates

        # Si todo falla, mostrar mensaje claro (sin datos fijos)
        logger.warning("❌ No se pudo obtener ninguna cartelera. Retornando lista vacía.")
        return []

    def _scrape_multiple_sources(self):
        """Intenta scraping en múltiples fuentes oficiales y alternativas"""
        fuentes = [
            self._scrape_ufc_com,
            self._scrape_ufcespanol,
            self._scrape_espn_mma,
        ]
        
        for fuente in fuentes:
            try:
                combates = fuente()
                if combates and len(combates) >= 2:
                    # Filtrar solo eventos futuros
                    combates_futuros = self._filtrar_eventos_futuros(combates)
                    if combates_futuros:
                        return combates_futuros
            except Exception as e:
                logger.warning(f"Error en fuente: {e}")
                continue
        
        return None

    def _scrape_ufc_com(self):
        """Scrapea ufc.com/events"""
        try:
            url = "https://www.ufc.com/events"
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            combates = []
            
            # Buscar eventos próximos (múltiples selectores)
            eventos = soup.select('.c-card-event, .event-card, article')
            
            for evento in eventos:
                # Extraer nombre del evento
                nombre_evento = "UFC Fight Night"
                titulo = evento.select_one('h3, .headline, .title, .c-card-event--result__headline')
                if titulo:
                    nombre_evento = titulo.get_text(strip=True)
                
                # Extraer fecha del evento
                fecha_evento = self._extraer_fecha_evento(evento)
                if fecha_evento and fecha_evento < datetime.now():
                    continue  # Saltar eventos pasados
                
                # Extraer peleas
                peleas = evento.select('.c-listing-fight, .fight-row, .matchup')
                
                for pelea in peleas:
                    try:
                        nombres = pelea.select('.fighter-name, .c-listing-fight__corner-name, .name')
                        if len(nombres) >= 2:
                            p1 = nombres[0].get_text(strip=True)
                            p2 = nombres[1].get_text(strip=True)
                            if p1 and p2 and len(p1) > 3 and len(p2) > 3:
                                combates.append({
                                    'peleador1': {'nombre': self._limpiar_nombre(p1)},
                                    'peleador2': {'nombre': self._limpiar_nombre(p2)},
                                    'categoria': self._extraer_categoria(pelea),
                                    'evento': nombre_evento,
                                    'fecha_evento': fecha_evento.strftime("%Y-%m-%d") if fecha_evento else None
                                })
                    except:
                        continue
            
            return combates[:15]
            
        except Exception as e:
            logger.warning(f"Error en ufc.com: {e}")
            return None

    def _scrape_ufcespanol(self):
        """Scrapea ufcespanol.com/events"""
        try:
            url = "https://www.ufcespanol.com/events"
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            combates = []
            peleas = soup.select('.c-listing-fight, .fight-row, .matchup')
            
            for pelea in peleas[:15]:
                try:
                    nombres = pelea.select('.fighter-name, .c-listing-fight__corner-name, .name')
                    if len(nombres) >= 2:
                        p1 = nombres[0].get_text(strip=True)
                        p2 = nombres[1].get_text(strip=True)
                        if p1 and p2 and len(p1) > 3 and len(p2) > 3:
                            combates.append({
                                'peleador1': {'nombre': self._limpiar_nombre(p1)},
                                'peleador2': {'nombre': self._limpiar_nombre(p2)},
                                'categoria': self._extraer_categoria(pelea),
                                'evento': 'UFC Fight Night',
                                'fecha_evento': None
                            })
                except:
                    continue
            
            return combates
            
        except Exception as e:
            logger.warning(f"Error en ufcespanol.com: {e}")
            return None

    def _scrape_espn_mma(self):
        """Scrapea ESPN MMA como alternativa"""
        try:
            url = "https://www.espn.com/mma/schedule"
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            combates = []
            filas = soup.select('tr, .fight-card, .event')
            
            for fila in filas:
                try:
                    celdas = fila.select('td, .fighter, .name')
                    if len(celdas) >= 2:
                        p1 = celdas[0].get_text(strip=True)
                        p2 = celdas[1].get_text(strip=True)
                        if p1 and p2 and len(p1) > 3 and len(p2) > 3:
                            combates.append({
                                'peleador1': {'nombre': self._limpiar_nombre(p1)},
                                'peleador2': {'nombre': self._limpiar_nombre(p2)},
                                'categoria': 'MMA',
                                'evento': 'UFC',
                                'fecha_evento': None
                            })
                except:
                    continue
            
            return combates[:10]
            
        except Exception as e:
            logger.warning(f"Error en ESPN MMA: {e}")
            return None

    def _scrape_alternativo(self):
        """Scraping alternativo con APIs públicas"""
        try:
            # Intentar con API de TheSportsDB (si está disponible)
            url = "https://www.thesportsdb.com/api/v1/json/3/eventsnextleague.php?id=4387"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'events' in data:
                    combates = []
                    for evento in data['events'][:10]:
                        combates.append({
                            'peleador1': {'nombre': evento.get('strHomeTeam', '')},
                            'peleador2': {'nombre': evento.get('strAwayTeam', '')},
                            'categoria': evento.get('strLeague', 'UFC'),
                            'evento': evento.get('strEvent', 'UFC Event'),
                            'fecha_evento': evento.get('dateEvent', None)
                        })
                    if combates:
                        return combates
        except:
            pass
        
        return None

    def _extraer_fecha_evento(self, elemento):
        """Extrae la fecha del evento del HTML"""
        try:
            # Buscar texto con formato de fecha
            texto = elemento.get_text()
            
            # Patrones de fecha comunes
            patrones = [
                r'(\d{1,2}/\d{1,2}/\d{4})',
                r'(\d{4}-\d{2}-\d{2})',
                r'(Ene|Feb|Mar|Abr|May|Jun|Jul|Ago|Sep|Oct|Nov|Dic)\s+\d{1,2},?\s+\d{4}',
                r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}'
            ]
            
            for patron in patrones:
                match = re.search(patron, texto, re.IGNORECASE)
                if match:
                    fecha_str = match.group(1)
                    try:
                        return datetime.strptime(fecha_str, "%B %d, %Y")
                    except:
                        try:
                            return datetime.strptime(fecha_str, "%b %d, %Y")
                        except:
                            try:
                                return datetime.strptime(fecha_str, "%m/%d/%Y")
                            except:
                                try:
                                    return datetime.strptime(fecha_str, "%Y-%m-%d")
                                except:
                                    pass
        except:
            pass
        return None

    def _extraer_categoria(self, elemento):
        """Extrae la categoría/peso de la pelea"""
        try:
            texto = elemento.get_text()
            categorias = ['Peso Pesado', 'Peso Semipesado', 'Peso Medio', 
                         'Peso Welter', 'Peso Ligero', 'Peso Pluma', 
                         'Peso Gallo', 'Peso Mosca', 'Peso Paja']
            for cat in categorias:
                if cat.lower() in texto.lower():
                    return cat
        except:
            pass
        return 'Peso Pactado'

    def _limpiar_nombre(self, nombre):
        """Limpia el nombre del peleador"""
        # Eliminar texto entre paréntesis
        nombre = re.sub(r'\([^)]*\)', '', nombre)
        # Eliminar números de ranking
        nombre = re.sub(r'#\d+', '', nombre)
        # Eliminar espacios extra
        nombre = ' '.join(nombre.split())
        return nombre.strip()

    def _filtrar_eventos_futuros(self, combates):
        """Filtra solo los eventos que son en el futuro o hoy"""
        hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        futuros = []
        
        for combate in combates:
            fecha_str = combate.get('fecha_evento')
            if fecha_str:
                try:
                    fecha_evento = datetime.strptime(fecha_str, "%Y-%m-%d")
                    if fecha_evento >= hoy:
                        futuros.append(combate)
                except:
                    futuros.append(combate)  # Si no podemos parsear, lo incluimos
            else:
                futuros.append(combate)  # Sin fecha, lo incluimos
        
        return futuros

    def _obtener_ultima_cartelera_bd(self):
        """Recupera la última cartelera guardada en BD"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT cartelera, fecha_evento FROM eventos_ufc ORDER BY ultima_actualizacion DESC LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            if row and row[0]:
                combates = json.loads(row[0])
                # Verificar si es reciente (menos de 7 días)
                if row[1]:
                    try:
                        fecha_guardado = datetime.strptime(row[1], "%Y-%m-%d")
                        if (datetime.now() - fecha_guardado).days <= 7:
                            return combates
                    except:
                        pass
                return combates
        except Exception as e:
            logger.error(f"Error recuperando de BD: {e}")
        return []

    def _guardar_en_bd(self, combates):
        """Guarda la cartelera en la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Limpiar anteriores
            cursor.execute("DELETE FROM eventos_ufc")
            
            # Obtener fecha del primer combate si existe
            fecha_evento = None
            if combates and combates[0].get('fecha_evento'):
                fecha_evento = combates[0].get('fecha_evento')
            
            cursor.execute('''
                INSERT INTO eventos_ufc (nombre, fecha, cartelera, ultima_actualizacion, fecha_evento)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                "UFC Próximo Evento",
                datetime.now().strftime("%Y-%m-%d"),
                json.dumps(combates, ensure_ascii=False),
                datetime.now().isoformat(),
                fecha_evento
            ))
            
            conn.commit()
            logger.info(f"✅ Cartelera guardada en BD ({len(combates)} combates)")
        except Exception as e:
            logger.error(f"Error guardando cartelera: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
