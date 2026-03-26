# -*- coding: utf-8 -*-
"""
SCRAPER ODDS UFC MEJORADO - Desde Action Network con Selenium
Busca en la página del evento específico para obtener TODOS los odds
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

class ScraperOddsUFCCompleto:
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
        """Obtiene odds de UFC desde Action Network (evento específico)"""
        # URL del evento UFC Fight Night: Adesanya vs Pyfer
        url = "https://www.actionnetwork.com/ufc/ufc-fight-night-adesanya-vs-pyfer-odds"
        
        print(f"📡 Extrayendo odds desde evento específico...")
        
        try:
            self.driver.get(url)
            time.sleep(5)
            
            # Hacer scroll para cargar todo
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            odds = {}
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Buscar patrones de la imagen
            # Patrón: "Tyrell Fortune: -132" o "Tyrell Fortune -132"
            patron1 = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+(?:\.)?))\s*:?\s*([+-]\d{3,4})'
            matches = re.findall(patron1, page_text)
            for nombre, odd in matches:
                odds[nombre.lower()] = odd
            
            # Patrón 2: nombres con apellidos compuestos
            patron2 = r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+([+-]\d+)'
            matches2 = re.findall(patron2, page_text)
            for nombre, odd in matches2:
                odds[nombre.lower()] = odd
            
            # Patrón 3: odds en líneas específicas
            lineas = page_text.split('\n')
            for i, linea in enumerate(lineas):
                # Buscar línea con formato "Nombre: +120"
                match = re.match(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*:\s*([+-]\d+)$', linea.strip())
                if match:
                    nombre = match.group(1).strip()
                    odd = match.group(2).strip()
                    odds[nombre.lower()] = odd
            
            print(f"✅ Encontrados {len(odds)} odds totales")
            return odds
            
        except Exception as e:
            print(f"❌ Error extrayendo odds: {e}")
            return {}
        finally:
            self.driver.quit()
    
    def obtener_odds_para_cartelera(self):
        """Obtiene odds específicas para los peleadores de la cartelera actual"""
        peleadores = self._obtener_peleadores_desde_bd()
        
        if not peleadores:
            print("⚠️ No hay peleadores en la BD. Ejecuta primero: python cargar_ufc_json.py")
            return {}
        
        print(f"📡 Buscando odds para {len(peleadores)} peleadores...")
        
        odds_totales = self.obtener_odds()
        
        # Si no encontró odds en evento específico, usar página principal
        if not odds_totales:
            print("   No se encontraron odds en evento específico, probando página principal...")
            odds_totales = self._obtener_odds_principal()
        
        resultados = {}
        for peleador in peleadores:
            nombre_lower = peleador.lower()
            encontrado = False
            
            # Buscar coincidencia exacta o parcial
            for key, odd in odds_totales.items():
                if nombre_lower in key or key in nombre_lower:
                    resultados[peleador] = odd
                    encontrado = True
                    break
            
            if not encontrado:
                # Buscar por apellido
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
        
        # Mostrar resultados
        encontrados = sum(1 for v in resultados.values() if v != "N/A")
        print(f"✅ Encontrados {encontrados}/{len(peleadores)} odds")
        
        for nombre, odd in list(resultados.items())[:15]:
            print(f"   {nombre}: {odd}")
        
        return resultados
    
    def _obtener_odds_principal(self):
        """Fallback: obtener odds desde página principal"""
        url = "https://www.actionnetwork.com/ufc/odds"
        
        try:
            self.driver.get(url)
            time.sleep(5)
            
            odds = {}
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            patron = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+([+-]\d+)'
            matches = re.findall(patron, page_text)
            for nombre, odd in matches:
                odds[nombre.lower()] = odd
            
            return odds
        except:
            return {}
    
    def guardar_odds_en_bd(self, odds):
        """Guarda los odds en la BD"""
        conn = sqlite3.connect("data/betting_stats.db")
        cursor = conn.cursor()
        
        # Agregar columna odds si no existe
        try:
            cursor.execute("ALTER TABLE peleadores_ufc ADD COLUMN odds TEXT")
        except:
            pass
        
        for nombre, odd in odds.items():
            if odd != "N/A":
                cursor.execute('''
                    UPDATE peleadores_ufc SET odds = ? WHERE nombre = ?
                ''', (odd, nombre))
        
        conn.commit()
        conn.close()
        print(f"✅ {len([v for v in odds.values() if v != 'N/A'])} odds guardados en BD")

def actualizar_odds_ufc():
    scraper = ScraperOddsUFCCompleto()
    odds = scraper.obtener_odds_para_cartelera()
    
    if odds:
        scraper.guardar_odds_en_bd(odds)
    
    return odds

if __name__ == "__main__":
    odds = actualizar_odds_ufc()
    
    print("\n📊 RESULTADO FINAL:")
    for nombre, odd in odds.items():
        print(f"   {nombre}: {odd}")
