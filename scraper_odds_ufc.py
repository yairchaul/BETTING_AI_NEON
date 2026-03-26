# -*- coding: utf-8 -*-
"""
SCRAPER ODDS UFC DINÁMICO - Extrae odds de Caliente.mx para cualquier cartelera
No usa nombres fijos, los toma desde eventos_ufc.json
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

class ScraperOddsUFC:
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
    
    def _obtener_peleadores_desde_bd(self):
        """Obtiene la lista de peleadores desde la BD (último evento)"""
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
    
    def obtener_odds(self):
        """Obtiene odds de UFC desde Caliente.mx"""
        # Primero obtener los nombres de los peleadores
        peleadores = self._obtener_peleadores_desde_bd()
        
        if not peleadores:
            print("⚠️ No hay peleadores en la BD. Ejecuta primero: python cargar_ufc_json.py")
            return {}
        
        print(f"📡 Buscando odds para {len(peleadores)} peleadores...")
        
        url = "https://www.caliente.mx/es/mx/ufc-mma"
        
        try:
            self.driver.get(url)
            time.sleep(5)
            
            # Hacer scroll para cargar todo
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            odds = {}
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Buscar odds para cada peleador dinámicamente
            for peleador in peleadores:
                # Limpiar nombre para buscar
                nombre_limpio = peleador.lower().strip()
                
                # Patrón 1: nombre + odd (ej: "alexia thainara -900")
                patron1 = rf'{re.escape(peleador)}[^\n]*?([+-]\d+)'
                match1 = re.search(patron1, page_text, re.IGNORECASE)
                if match1:
                    odds[peleador] = match1.group(1)
                    continue
                
                # Patrón 2: odd + nombre
                patron2 = rf'([+-]\d+)[^\n]*?{re.escape(peleador)}'
                match2 = re.search(patron2, page_text, re.IGNORECASE)
                if match2:
                    odds[peleador] = match2.group(1)
                    continue
                
                # Patrón 3: buscar por partes del nombre (primer apellido)
                partes = peleador.split()
                if len(partes) > 1:
                    apellido = partes[-1]
                    patron3 = rf'{apellido}[^\n]*?([+-]\d+)'
                    match3 = re.search(patron3, page_text, re.IGNORECASE)
                    if match3:
                        odds[peleador] = match3.group(1)
                        continue
                
                # Patrón 4: buscar en líneas específicas
                lineas = page_text.split('\n')
                for i, linea in enumerate(lineas):
                    if peleador.lower() in linea.lower():
                        # Buscar odd en la misma línea o en las cercanas
                        for j in range(max(0, i-2), min(len(lineas), i+3)):
                            odd_match = re.search(r'([+-]\d{3,4})', lineas[j])
                            if odd_match:
                                odds[peleador] = odd_match.group(1)
                                break
                        break
            
            # Mostrar resultados
            encontrados = sum(1 for v in odds.values() if v)
            print(f"✅ Encontrados {encontrados}/{len(peleadores)} odds")
            
            for peleador in peleadores[:10]:
                odd = odds.get(peleador, 'N/A')
                print(f"   {peleador}: {odd}")
            
            return odds
            
        except Exception as e:
            print(f"❌ Error extrayendo odds: {e}")
            return {}
        finally:
            self.driver.quit()
    
    def guardar_odds_en_bd(self, odds):
        """Guarda los odds en la BD junto con los peleadores"""
        conn = sqlite3.connect("data/betting_stats.db")
        cursor = conn.cursor()
        
        # Agregar columna odds si no existe
        try:
            cursor.execute("ALTER TABLE peleadores_ufc ADD COLUMN odds TEXT")
        except:
            pass
        
        for nombre, odd in odds.items():
            cursor.execute('''
                UPDATE peleadores_ufc SET odds = ? WHERE nombre = ?
            ''', (odd, nombre))
        
        conn.commit()
        conn.close()
        print(f"✅ {len(odds)} odds guardados en BD")

def actualizar_odds_ufc():
    """Actualiza odds para todos los peleadores del último evento"""
    scraper = ScraperOddsUFC()
    odds = scraper.obtener_odds()
    
    if odds:
        scraper.guardar_odds_en_bd(odds)
    
    return odds

if __name__ == "__main__":
    odds = actualizar_odds_ufc()
    
    print("\n📊 Resumen:")
    for nombre, odd in odds.items():
        print(f"   {nombre}: {odd}")
