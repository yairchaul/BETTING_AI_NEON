# -*- coding: utf-8 -*-
"""
ESPN_UFC - Scraper Definitivo y Automático (Sin datos fijos nunca)
Versión optimizada con scraping real + fallback a BD
"""

import requests
from bs4 import BeautifulSoup
import json
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ESPN_UFC:
    def __init__(self):
        self.db_path = 'data/betting_stats.db'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0 Safari/537.36'
        }
        self._crear_tablas()

    def _crear_tablas(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS eventos_ufc (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT,
                    fecha TEXT,
                    cartelera TEXT,
                    ultima_actualizacion TEXT
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
        """Obtiene la cartelera real más reciente"""
        logger.info("🔍 Buscando cartelera UFC actual...")

        # Intento 1: Scrape real
        combates = self._scrape_real()

        if combates and len(combates) >= 2:
            logger.info(f"✅ Cartelera real obtenida ({len(combates)} combates)")
            self._guardar_en_bd(combates)
            return combates

        # Intento 2: Última cartelera guardada en BD
        logger.warning("⚠️ Scraper web falló. Recuperando última cartelera guardada...")
        combates = self._obtener_ultima_cartelera_bd()

        if combates:
            return combates

        # Último recurso: mensaje claro (nunca datos fijos)
        logger.warning("⚠️ No se encontró cartelera reciente")
        return []

    def _scrape_real(self):
        """Intenta scraping en fuentes oficiales"""
        urls = [
            "https://www.ufc.com/events",
            "https://www.ufcespanol.com/events",
        ]

        for url in urls:
            try:
                response = requests.get(url, headers=self.headers, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                combates = []
                peleas = soup.select('.c-listing-fight, .fight-row, .matchup, .c-card-fight')

                for pelea in peleas[:12]:
                    try:
                        nombres = pelea.select('.fighter-name, .c-listing-fight__corner-name, .name')
                        if len(nombres) >= 2:
                            p1 = nombres[0].get_text(strip=True)
                            p2 = nombres[1].get_text(strip=True)
                            if p1 and p2 and len(p1) > 3 and len(p2) > 3:
                                combates.append({
                                    'peleador1': {'nombre': p1},
                                    'peleador2': {'nombre': p2},
                                    'categoria': 'Peso Pactado',
                                    'evento': 'UFC Próximo Evento',
                                    'fecha': datetime.now().strftime("%Y-%m-%d")
                                })
                    except:
                        continue

                if combates:
                    return combates
            except Exception as e:
                logger.warning(f"Error en {url}: {e}")
                continue

        return None

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
            ''', (
                "UFC Próximo Evento",
                datetime.now().strftime("%Y-%m-%d"),
                json.dumps(combates, ensure_ascii=False),
                datetime.now().isoformat()
            ))
            conn.commit()
            logger.info(f"✅ Cartelera guardada en BD ({len(combates)} combates)")
        except Exception as e:
            logger.error(f"Error guardando cartelera: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
