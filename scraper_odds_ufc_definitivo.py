# -*- coding: utf-8 -*-
"""
SCRAPER ODDS UFC DEFINITIVO - Desde Action Network
Extrae odds de la tabla estructurada correctamente
URL: https://www.actionnetwork.com/ufc/odds
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
        """Obtiene odds de UFC desde Action Network"""
        url = "https://www.actionnetwork.com/ufc/odds"
        
        print(f"📡 Extrayendo odds desde Action Network...")
        
        try:
            self.driver.get(url)
            time.sleep(5)
            
            # Hacer scroll para cargar todo
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            odds = {}
            
            # Buscar la tabla de odds
            # Los odds están en filas con información de peleadores
            filas = self.driver.find_elements(By.CSS_SELECTOR, "tr, .event-row, .odds-row")
            
            for fila in filas:
                texto_fila = fila.text
                
                # Patrón de la imagen: "+390 -520" o "+525 -700"
                # Buscar dos odds en la misma línea (peleador1 vs peleador2)
                patron_doble = r'([+-]\d{3,4})\s+([+-]\d{3,4})'
                odds_dobles = re.findall(patron_doble, texto_fila)
                
                if odds_dobles:
                    # Buscar nombres de peleadores en la misma fila o cercanos
                    # Los nombres suelen estar antes de los odds
                    nombres = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', texto_fila)
                    
                    # Filtrar nombres válidos (más de 3 letras, no odds)
                    nombres_validos = [n for n in nombres if len(n) > 3 and not n.startswith(('+', '-'))]
                    
                    for i, odd_pair in enumerate(odds_dobles):
                        if len(nombres_validos) >= i*2 + 2:
                            p1 = nombres_validos[i*2]
                            p2 = nombres_validos[i*2 + 1]
                            odds[p1.lower()] = odd_pair[0]
                            odds[p2.lower()] = odd_pair[1]
            
            # Método 2: Buscar por la estructura que vemos en la imagen
            # Cada pelea tiene un horario y luego los odds
            lineas = self.driver.find_element(By.TAG_NAME, "body").text.split('\n')
            
            for i, linea in enumerate(lineas):
                # Buscar líneas con formato de horario (Sun 3/29, 5:00 AM)
                if re.match(r'\w+\s+\d+/\d+,\s+\d+:\d+\s+[AP]M', linea):
                    # La siguiente línea contiene los nombres y odds
                    if i + 1 < len(lineas):
                        datos_linea = lineas[i + 1]
                        # Buscar pares de nombres y odds
                        # Patrón: "+390 -520" indica que hay dos peleadores
                        odds_encontrados = re.findall(r'([+-]\d{3,4})', datos_linea)
                        nombres_encontrados = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', datos_linea)
                        
                        # Filtrar nombres válidos
                        nombres_validos = [n for n in nombres_encontrados if len(n) > 3]
                        
                        for j in range(min(len(odds_encontrados) // 2, len(nombres_validos) // 2)):
                            if j * 2 + 1 < len(odds_encontrados) and j * 2 + 1 < len(nombres_validos):
                                p1 = nombres_validos[j*2]
                                p2 = nombres_validos[j*2 + 1]
                                odd1 = odds_encontrados[j*2]
                                odd2 = odds_encontrados[j*2 + 1]
                                odds[p1.lower()] = odd1
                                odds[p2.lower()] = odd2
            
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
    scraper = ScraperOddsUFCDefinitivo()
    odds = scraper.obtener_odds_para_cartelera()
    
    if odds:
        scraper.guardar_odds_en_bd(odds)
    
    return odds

if __name__ == "__main__":
    odds = actualizar_odds_ufc()
    
    print("\n📊 RESULTADO FINAL:")
    for nombre, odd in odds.items():
        print(f"   {nombre}: {odd}")
