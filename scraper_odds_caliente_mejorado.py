# -*- coding: utf-8 -*-
"""
SCRAPER ODDS UFC MEJORADO - Caliente.mx con Selenium
Extrae todos los odds de la cartelera actual
"""

import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class ScraperOddsCalienteMejorado:
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
    
    def obtener_odds_ufc(self):
        """Obtiene todos los odds de UFC desde Caliente.mx"""
        url = "https://www.caliente.mx/es/mx/ufc-mma"
        
        print(f"📡 Extrayendo odds desde Caliente.mx...")
        
        try:
            self.driver.get(url)
            time.sleep(5)
            
            odds = {}
            
            # Hacer scroll para cargar todo
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Método 1: Buscar en la estructura de eventos
            # Buscar el evento UFC Fight Night: Adesanya vs Pyfer
            eventos = self.driver.find_elements(By.CSS_SELECTOR, "[class*='event'], [class*='matchup']")
            
            for evento in eventos:
                texto = evento.text
                # Buscar el nombre del evento que contiene los peleadores que queremos
                if "Adesanya" in texto or "Pyfer" in texto:
                    # Buscar líneas con odds
                    lineas = texto.split('\n')
                    for i, linea in enumerate(lineas):
                        # Patrón: nombre + odd (ej: "Alexia Thainara -900")
                        match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+([+-]\d+)', linea)
                        if match:
                            nombre = match.group(1).strip()
                            odd = match.group(2).strip()
                            odds[nombre.lower()] = odd
                        
                        # Patrón alternativo: odd + nombre
                        match2 = re.search(r'([+-]\d+)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', linea)
                        if match2:
                            odd = match2.group(1).strip()
                            nombre = match2.group(2).strip()
                            odds[nombre.lower()] = odd
            
            # Método 2: Buscar en toda la página con regex avanzado
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Buscar patrones de peleadores conocidos
            peleadores_conocidos = [
                "Alexia Thainara", "Bruna Brasil", "Ricky Simon", "Adrian Yanez",
                "Navajo Stirling", "Bruno Lopes", "Casey O'Neill", "Gabriella Fernandes",
                "Marcin Tybura", "Tyrell Fortune", "Chase Hooper", "Lance Gibson Jr.",
                "Ignacio Bahamondes", "Tofiq Musayev", "Terrance McKinney", "Kyle Nelson",
                "Mansur Abdul-Malik", "Yousri Belgaroui", "Julian Erosa", "Lerryan Douglas",
                "Michael Chiesa", "Niko Price", "Alexa Grasso", "Maycee Barber",
                "Israel Adesanya", "Joe Pyfer"
            ]
            
            for peleador in peleadores_conocidos:
                # Buscar el odd cerca del nombre
                patron = rf'{peleador}[^\n]*?([+-]\d+)'
                match = re.search(patron, page_text, re.IGNORECASE)
                if match:
                    odds[peleador.lower()] = match.group(1)
                
                # Patrón alternativo (odd primero)
                patron2 = rf'([+-]\d+)[^\n]*?{peleador}'
                match2 = re.search(patron2, page_text, re.IGNORECASE)
                if match2 and peleador.lower() not in odds:
                    odds[peleador.lower()] = match2.group(1)
            
            print(f"✅ Encontrados {len(odds)} odds")
            return odds
            
        except Exception as e:
            print(f"❌ Error extrayendo odds: {e}")
            return {}
        finally:
            self.driver.quit()

def obtener_odds_para_cartelera(cartelera):
    """Obtiene odds para todos los peleadores de una cartelera"""
    scraper = ScraperOddsCalienteMejorado()
    odds_totales = scraper.obtener_odds_ufc()
    
    resultados = {}
    for pelea in cartelera:
        p1 = pelea.get('peleador1', '')
        p2 = pelea.get('peleador2', '')
        
        odd1 = None
        odd2 = None
        
        for nombre, odd in odds_totales.items():
            if p1.lower() in nombre or nombre in p1.lower():
                odd1 = odd
            if p2.lower() in nombre or nombre in p2.lower():
                odd2 = odd
        
        resultados[p1] = odd1
        resultados[p2] = odd2
        print(f"   {p1}: {odd1 if odd1 else 'N/A'} | {p2}: {odd2 if odd2 else 'N/A'}")
    
    return resultados

if __name__ == "__main__":
    scraper = ScraperOddsCalienteMejorado()
    odds = scraper.obtener_odds_ufc()
    
    print("\n📊 Odds encontradas:")
    for nombre, odd in list(odds.items())[:30]:
        print(f"   {nombre}: {odd}")
