# -*- coding: utf-8 -*-
"""
ESPN UFC - Módulo unificado con Selenium (local) y API fallback (Cloud)
Funciona en local con Selenium, en Cloud con API de ESPN
"""

import json
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ESPN_UFC:
    def __init__(self):
        self.db_path = 'data/betting_stats.db'
        self._crear_tablas()
        self._selenium_disponible = self._verificar_selenium()
    
    def _verificar_selenium(self):
        """Verifica si Selenium está disponible (solo en local)"""
        try:
            import selenium
            # Intentar importar webdriver_manager
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                return True
            except:
                return False
        except ImportError:
            return False
    
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
        """Obtiene la cartelera - Selenium en local, API en Cloud"""
        logger.info("🔍 Obteniendo cartelera UFC...")
        
        # Intento 1: Selenium (solo si está disponible)
        if self._selenium_disponible:
            combates = self._scrapear_con_selenium()
            if combates:
                logger.info(f"✅ Cartelera obtenida con Selenium: {len(combates)} combates")
                self._guardar_en_bd(combates)
                return combates
        
        # Intento 2: API de ESPN (funciona en Cloud)
        combates = self._scrapear_con_api()
        if combates:
            logger.info(f"✅ Cartelera obtenida con API: {len(combates)} combates")
            self._guardar_en_bd(combates)
            return combates
        
        # Intento 3: BD como fallback
        logger.info("📀 Recuperando última cartelera guardada...")
        return self._obtener_ultima_cartelera_bd()

    def _scrapear_con_selenium(self):
        """Usa Selenium para extraer odds (funciona en local)"""
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            # Buscar evento activo
            url = "https://www.espn.com.mx/mma/fightcenter/_/id/600058693/liga/ufc"
            driver.get(url)
            
            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "FightCard")))
            
            combates = []
            fight_cards = driver.find_elements(By.CLASS_NAME, "FightCard")
            
            for card in fight_cards[:15]:
                try:
                    fighters = card.find_elements(By.CSS_SELECTOR, ".fighter-name")
                    if len(fighters) >= 2:
                        p1 = fighters[0].text.strip()
                        p2 = fighters[1].text.strip()
                        
                        # Extraer odds
                        odds_elements = card.find_elements(By.CSS_SELECTOR, ".odds")
                        odds1 = odds_elements[0].text.strip() if len(odds_elements) > 0 else "N/A"
                        odds2 = odds_elements[1].text.strip() if len(odds_elements) > 1 else "N/A"
                        
                        combates.append({
                            'peleador1': {'nombre': p1},
                            'peleador2': {'nombre': p2},
                            'categoria': 'Peso Pactado',
                            'odds': {'moneyline_local': odds1, 'moneyline_visitante': odds2},
                            'fecha_evento': datetime.now().strftime("%Y-%m-%d")
                        })
                except:
                    continue
            
            driver.quit()
            return combates
            
        except Exception as e:
            logger.error(f"Error en Selenium: {e}")
            return []

    def _scrapear_con_api(self):
        """Usa API de ESPN (funciona en Cloud)"""
        try:
            import requests
            api_url = "https://site.api.espn.com/apis/site/v2/sports/mma/ufc/scoreboard"
            response = requests.get(api_url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                combates = []
                
                for event in data.get('events', []):
                    nombre_evento = event.get('name', 'UFC Event')
                    fecha_evento = event.get('date', '')[:10]
                    
                    for comp in event.get('competitions', []):
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
                return combates
        except Exception as e:
            logger.error(f"Error en API: {e}")
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
            ''', ("UFC", datetime.now().strftime("%Y-%m-%d"), json.dumps(combates), datetime.now().isoformat()))
            conn.commit()
        except Exception as e:
            logger.error(f"Error guardando: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
