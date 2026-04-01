# -*- coding: utf-8 -*-
"""
SCRAPER ODDS UFC DEFINITIVO - Desde Action Network con URL dinámica
"""

import time
import re
import json
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class ScraperOddsUFCDefinitivo:
    def __init__(self):
        self._setup_driver()
    
    def _setup_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        print("✅ Chrome driver iniciado")
    
    def _obtener_evento_actual(self):
        """Obtiene el nombre del evento más reciente desde la BD"""
        try:
            conn = sqlite3.connect("data/betting_stats.db")
            cursor = conn.cursor()
            cursor.execute("SELECT nombre FROM eventos_ufc ORDER BY fecha DESC LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else None
        except Exception as e:
            print(f"Error leyendo BD: {e}")
            return None
    
    def _obtener_peleadores_desde_bd(self):
        try:
            conn = sqlite3.connect("data/betting_stats.db")
            cursor = conn.cursor()
            cursor.execute("SELECT cartelera FROM eventos_ufc ORDER BY fecha DESC LIMIT 1")
            evento = cursor.fetchone()
            conn.close()
            
            peleadores = []
            if evento and evento[0]:
                cartelera = json.loads(evento[0])
                for pelea in cartelera:
                    p1 = pelea.get('peleador1', '')
                    p2 = pelea.get('peleador2', '')
                    if p1:
                        peleadores.append(p1)
                    if p2:
                        peleadores.append(p2)
            return peleadores
        except Exception as e:
            print(f"Error leyendo BD: {e}")
            return []
    
    def obtener_odds(self):
        """Obtiene odds del evento actual desde Action Network (URL dinámica)"""
        nombre_evento = self._obtener_evento_actual()
        if not nombre_evento:
            print("⚠️ No hay evento en BD. Ejecuta primero crear_tabla_eventos_auto.py")
            return {}
        
        # Generar URL dinámica
        slug = nombre_evento.lower().replace(":", "").replace(".", "").replace(" ", "-")
        url = f"https://www.actionnetwork.com/ufc/{slug}-odds"
        
        print(f"📡 Evento: {nombre_evento}")
        print(f"🔗 URL: {url}")
        
        try:
            self.driver.get(url)
            time.sleep(5)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            odds = {}
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Patrón: nombre + odd
            patron = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+([+-]\d{3,4})'
            matches = re.findall(patron, page_text)
            for nombre, odd in matches:
                if len(nombre) > 3:
                    odds[nombre.lower()] = odd
            
            print(f"✅ {len(odds)} odds encontrados")
            return odds
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return {}
        finally:
            self.driver.quit()
    
    def obtener_odds_para_cartelera(self):
        peleadores = self._obtener_peleadores_desde_bd()
        if not peleadores:
            return {}
        
        odds_totales = self.obtener_odds()
        resultados = {}
        
        for peleador in peleadores:
            nombre_lower = peleador.lower()
            encontrado = False
            for key, odd in odds_totales.items():
                if nombre_lower in key or key in nombre_lower:
                    resultados[peleador] = odd
                    encontrado = True
                    break
            if not encontrado:
                partes = peleador.split()
                if len(partes) > 1:
                    apellido = partes[-1].lower()
                    for key, odd in odds_totales.items():
                        if apellido in key:
                            resultados[peleador] = odd
                            encontrado = True
                            break
            if not encontrado:
                resultados[peleador] = "N/A"
        
        print(f"✅ {sum(1 for v in resultados.values() if v != 'N/A')}/{len(peleadores)} odds")
        return resultados
    
    def guardar_odds_en_bd(self, odds):
        conn = sqlite3.connect("data/betting_stats.db")
        cursor = conn.cursor()
        try:
            cursor.execute("ALTER TABLE peleadores_ufc ADD COLUMN odds TEXT")
        except:
            pass
        
        for nombre, odd in odds.items():
            if odd != "N/A":
                cursor.execute("UPDATE peleadores_ufc SET odds = ? WHERE nombre = ?", (odd, nombre))
        
        conn.commit()
        conn.close()
        print(f"✅ {len([v for v in odds.values() if v != 'N/A'])} odds guardados")

def actualizar_odds_ufc():
    scraper = ScraperOddsUFCDefinitivo()
    odds = scraper.obtener_odds_para_cartelera()
    if odds:
        scraper.guardar_odds_en_bd(odds)
    return odds

if __name__ == "__main__":
    odds = actualizar_odds_ufc()
    for nombre, odd in odds.items():
        print(f"   {nombre}: {odd}")
