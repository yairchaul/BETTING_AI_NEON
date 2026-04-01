# -*- coding: utf-8 -*-
"""
ESPN UFC - Scraper Definitivo con ESPN FightCenter
100% DINÁMICO - Obtiene cartelera real y conecta con BD de peleadores
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

    def _obtener_datos_peleador(self, nombre):
        """Busca los datos del peleador en la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Búsqueda exacta o por LIKE
            cursor.execute('''
                SELECT nombre, record, altura, peso, alcance, postura, ko_rate, grappling, odds
                FROM peleadores_ufc 
                WHERE nombre = ? OR nombre LIKE ? OR ? LIKE '%' || nombre || '%'
                LIMIT 1
            ''', (nombre, f'%{nombre}%', nombre))
            
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
        except Exception as e:
            logger.debug(f"Error buscando peleador {nombre}: {e}")
            return None

    def get_events(self):
        """Obtiene la cartelera actual desde ESPN FightCenter"""
        logger.info("🔍 Obteniendo cartelera UFC desde ESPN FightCenter...")
        
        # Intentar scraping desde ESPN
        combates_raw = self._scrape_espn_fightcenter()
        
        if combates_raw and len(combates_raw) >= 2:
            logger.info(f"✅ Cartelera ESPN obtenida: {len(combates_raw)} combates")
            
            # ENRIQUECER con datos de la BD
            combates_enriquecidos = []
            for c in combates_raw:
                # Buscar datos de peleador1 en BD
                p1_nombre = c.get('peleador1', {}).get('nombre', '')
                p2_nombre = c.get('peleador2', {}).get('nombre', '')
                
                datos_p1 = self._obtener_datos_peleador(p1_nombre)
                datos_p2 = self._obtener_datos_peleador(p2_nombre)
                
                # Crear estructura completa
                combate_completo = {
                    'peleador1': datos_p1 if datos_p1 else {'nombre': p1_nombre},
                    'peleador2': datos_p2 if datos_p2 else {'nombre': p2_nombre},
                    'categoria': c.get('categoria', 'Peso Pactado'),
                    'evento': c.get('evento', 'UFC Fight Night'),
                    'fecha_evento': c.get('fecha_evento')
                }
                combates_enriquecidos.append(combate_completo)
            
            self._guardar_en_bd(combates_enriquecidos)
            self.eventos_cache = combates_enriquecidos
            return combates_enriquecidos
        
        # Fallback: recuperar de BD
        logger.info("📀 Recuperando última cartelera guardada...")
        combates = self._obtener_ultima_cartelera_bd()
        
        if combates:
            return combates
        
        logger.warning("❌ No se pudo obtener cartelera")
        return []

    def _scrape_espn_fightcenter(self):
        """Scrapea el FightCenter de ESPN para UFC"""
        # URL del evento actual desde ESPN México
        urls = [
            "https://www.espn.com.mx/mma/fightcenter/_/id/600058693/liga/ufc",
            "https://www.espn.com/mma/fightcenter",
        ]
        
        for url in urls:
            try:
                response = requests.get(url, headers=self.headers, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                combates = []
                
                # Extraer nombre del evento
                nombre_evento = "UFC Fight Night"
                titulo = soup.select_one('.headline h1, .event-title, .SectionHeader__title')
                if titulo:
                    nombre_evento = titulo.get_text(strip=True)
                    # Limpiar "Cobertura en vivo" etc.
                    nombre_evento = nombre_evento.replace("Cobertura de la pelea en vivo", "").strip()
                
                # Extraer fecha
                fecha_evento = self._extraer_fecha_espn(soup)
                
                # Buscar todas las peleas - múltiples selectores
                peleas = []
                
                # Selector para tarjeta principal
                main_card = soup.select('.main-card .fight-card, .main-event, .fightCard')
                peleas.extend(main_card)
                
                # Selector para prelims
                prelims = soup.select('.prelims .fight-card, .preliminary-card .fight')
                peleas.extend(prelims)
                
                # Selector genérico
                if not peleas:
                    peleas = soup.select('.fight-card, .matchupCard, .competitors, .fight')
                
                for pelea in peleas:
                    try:
                        # Extraer nombres - múltiples selectores
                        nombres = []
                        
                        # Intentar diferentes selectores
                        for selector in ['.fighter-name', '.competitor__name', '.name', '.athlete-name']:
                            noms = pelea.select(selector)
                            if len(noms) >= 2:
                                nombres = noms
                                break
                        
                        # Si no hay, buscar por texto
                        if len(nombres) < 2:
                            texto = pelea.get_text()
                            # Buscar patrones de nombres (dos palabras cada uno)
                            lines = [l.strip() for l in texto.split('\n') if l.strip()]
                            for line in lines:
                                if 'vs' in line.lower():
                                    parts = line.lower().split('vs')
                                    if len(parts) >= 2:
                                        p1 = parts[0].strip()
                                        p2 = parts[1].strip()
                                        if p1 and p2:
                                            nombres = [p1, p2]
                                            break
                        
                        if len(nombres) >= 2:
                            p1 = nombres[0].get_text(strip=True) if hasattr(nombres[0], 'get_text') else str(nombres[0])
                            p2 = nombres[1].get_text(strip=True) if hasattr(nombres[1], 'get_text') else str(nombres[1])
                            
                            # Limpiar nombres
                            p1 = self._limpiar_nombre(p1)
                            p2 = self._limpiar_nombre(p2)
                            
                            if p1 and p2 and len(p1) > 2 and len(p2) > 2:
                                # Extraer categoría
                                categoria = self._extraer_categoria_espn(pelea, soup)
                                
                                combates.append({
                                    'peleador1': {'nombre': p1},
                                    'peleador2': {'nombre': p2},
                                    'categoria': categoria,
                                    'evento': nombre_evento,
                                    'fecha_evento': fecha_evento
                                })
                    except Exception as e:
                        logger.debug(f"Error parseando pelea: {e}")
                        continue
                
                if combates:
                    logger.info(f"✅ Encontradas {len(combates)} peleas en {url}")
                    return combates
                    
            except Exception as e:
                logger.warning(f"Error en {url}: {e}")
                continue
        
        return None

    def _extraer_fecha_espn(self, soup):
        """Extrae la fecha del evento desde el HTML de ESPN"""
        try:
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

    def _extraer_categoria_espn(self, pelea, soup):
        """Extrae la categoría/peso de la pelea"""
        try:
            # Buscar en el elemento
            cat_elem = pelea.select_one('.weight-class, .category, .group-name, .weight')
            if cat_elem:
                return cat_elem.get_text(strip=True)
            
            # Buscar en el texto
            texto = pelea.get_text().lower()
            categorias = {
                'peso pesado': 'Peso Pesado',
                'heavyweight': 'Peso Pesado',
                'peso semipesado': 'Peso Semipesado',
                'light heavyweight': 'Peso Semipesado',
                'peso medio': 'Peso Medio',
                'middleweight': 'Peso Medio',
                'peso welter': 'Peso Welter',
                'welterweight': 'Peso Welter',
                'peso ligero': 'Peso Ligero',
                'lightweight': 'Peso Ligero',
                'peso pluma': 'Peso Pluma',
                'featherweight': 'Peso Pluma',
                'peso gallo': 'Peso Gallo',
                'bantamweight': 'Peso Gallo',
                'peso mosca': 'Peso Mosca',
                'flyweight': 'Peso Mosca',
                'peso paja': 'Peso Paja',
                'strawweight': 'Peso Paja'
            }
            
            for key, value in categorias.items():
                if key in texto:
                    return value
        except:
            pass
        return 'Peso Pactado'

    def _limpiar_nombre(self, nombre):
        """Limpia el nombre del peleador"""
        # Eliminar texto entre paréntesis
        nombre = re.sub(r'\([^)]*\)', '', nombre)
        # Eliminar emojis y caracteres especiales
        nombre = re.sub(r'[^\w\sáéíóúñÑ\.\-]', '', nombre)
        # Eliminar números de ranking
        nombre = re.sub(r'#\d+', '', nombre)
        # Eliminar texto "vs"
        nombre = re.sub(r'vs\.?\s*', '', nombre, flags=re.IGNORECASE)
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
