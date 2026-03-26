# -*- coding: utf-8 -*-
"""
SCRAPER ODDS UFC - Con Selenium para Caliente.mx
Carga la página completa con JavaScript
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import re

class ScraperOddsCalienteSelenium:
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
    
    def obtener_odds_ufc(self, evento="ufc-fight-night-adesanya-vs-pyfer"):
        """Obtiene odds de UFC desde Caliente.mx"""
        url = f"https://www.caliente.mx/es/mx/ufc-mma/{evento}"
        
        print(f"📡 Extrayendo odds desde Caliente.mx con Selenium...")
        
        try:
            self.driver.get(url)
            time.sleep(5)
            
            # Esperar a que carguen los odds
            wait = WebDriverWait(self.driver, 15)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            odds = {}
            
            # Buscar por diferentes selectores
            # Selector 1: Buscar por clase participant
            participantes = self.driver.find_elements(By.CSS_SELECTOR, "[class*='participant'], [class*='fighter'], [class*='competitor']")
            
            for p in participantes:
                texto = p.text
                # Buscar patrón: Nombre y odd (+123 o -123)
                match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*([+-]\d+)', texto)
                if match:
                    nombre = match.group(1).strip()
                    odd = match.group(2).strip()
                    odds[nombre.lower()] = odd
            
            # Selector 2: Buscar en toda la página
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            lineas = page_text.split('\n')
            
            for i, linea in enumerate(lineas):
                # Buscar líneas que contengan odds
                odd_match = re.search(r'([+-]\d{3,4})', linea)
                if odd_match:
                    odd = odd_match.group(1)
                    # Buscar el nombre en líneas anteriores/cercanas
                    for j in range(max(0, i-2), min(len(lineas), i+3)):
                        nombre_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', lineas[j])
                        if nombre_match and len(nombre_match.group(1)) > 3:
                            nombre = nombre_match.group(1).strip()
                            if nombre not in [k for k in odds.keys()]:
                                odds[nombre.lower()] = odd
                            break
            
            print(f"✅ Encontrados {len(odds)} odds")
            return odds
            
        except Exception as e:
            print(f"❌ Error extrayendo odds: {e}")
            return {}
        finally:
            self.driver.quit()

if __name__ == "__main__":
    scraper = ScraperOddsCalienteSelenium()
    odds = scraper.obtener_odds_ufc()
    
    print("\n📊 Odds encontradas:")
    for nombre, odd in list(odds.items())[:20]:
        print(f"   {nombre}: {odd}")
