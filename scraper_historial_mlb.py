# -*- coding: utf-8 -*-
"""
SCRAPER HISTÓRICO MLB - Basado en estructura real de ESPN
Extrae resultados: equipos y puntajes
"""

import sqlite3
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import re

class ScraperHistorialMLB:
    def __init__(self, db_path="data/betting_stats.db"):
        self.db_path = db_path
        self._init_db()
        self._setup_driver()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historial_equipos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_equipo TEXT NOT NULL,
                deporte TEXT NOT NULL,
                puntos_favor REAL,
                puntos_contra REAL,
                fecha TEXT,
                temporada TEXT
            )
        ''')
        conn.commit()
        conn.close()
        print("✅ Base de datos lista")
    
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
    
    def extraer_y_guardar(self, dias_atras=60):
        """Extrae resultados reales de los últimos N días"""
        fecha_hoy = datetime.now()
        total_guardados = 0
        
        for i in range(dias_atras):
            fecha = (fecha_hoy - timedelta(days=i)).strftime("%Y%m%d")
            url = f"https://www.espn.com.mx/beisbol/mlb/resultados/_/fecha/{fecha}"
            print(f"📡 MLB → {fecha}")
            
            try:
                self.driver.get(url)
                wait = WebDriverWait(self.driver, 12)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ScoreboardScoreCell")))
                time.sleep(2)
                
                # Buscar contenedores de partidos
                juegos = self.driver.find_elements(By.CLASS_NAME, "ScoreboardScoreCell")
                
                for juego in juegos:
                    try:
                        # Extraer texto completo del partido
                        texto = juego.text
                        lineas = texto.split('\n')
                        
                        # Buscar equipos y puntajes
                        equipo1 = None
                        equipo2 = None
                        puntaje1 = None
                        puntaje2 = None
                        
                        # El patrón en MLB: [Equipo1] (record) [puntaje] [H] [E] ... [Equipo2] (record) [puntaje] [H] [E]
                        # Buscar líneas que parezcan equipos (solo letras)
                        for j, linea in enumerate(lineas):
                            # Detectar nombre de equipo (solo letras, sin números)
                            if linea and linea[0].isalpha() and not any(c.isdigit() for c in linea):
                                if equipo1 is None:
                                    equipo1 = linea
                                elif equipo2 is None and linea != equipo1:
                                    equipo2 = linea
                            
                            # Detectar puntajes (números)
                            if linea.isdigit():
                                if puntaje1 is None:
                                    puntaje1 = int(linea)
                                elif puntaje2 is None:
                                    puntaje2 = int(linea)
                        
                        if equipo1 and equipo2 and puntaje1 is not None and puntaje2 is not None:
                            # Determinar local y visitante (por orden en la página)
                            # En MLB, el visitante aparece primero, local segundo
                            visitante = equipo1
                            local = equipo2
                            pts_visit = puntaje1
                            pts_local = puntaje2
                            
                            self._guardar_partido(visitante, "mlb", pts_visit, pts_local, fecha)
                            self._guardar_partido(local, "mlb", pts_local, pts_visit, fecha)
                            total_guardados += 2
                            print(f"   ✅ {local} {pts_local} - {pts_visit} {visitante}")
                            
                    except Exception as e:
                        print(f"   ⚠️ Error en partido: {e}")
                        continue
                
                time.sleep(1.5)
                
            except Exception as e:
                print(f"   ❌ Error en {fecha}: {e}")
        
        print(f"\n🏁 MLB histórico terminado. Total: {total_guardados} partidos guardados")
    
    def _guardar_partido(self, equipo, deporte, favor, contra, fecha):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO historial_equipos 
            (nombre_equipo, deporte, puntos_favor, puntos_contra, fecha, temporada)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (equipo, deporte, favor, contra, fecha, "2026"))
        conn.commit()
        conn.close()
    
    def cerrar(self):
        if self.driver:
            self.driver.quit()
            print("✅ Driver cerrado")

if __name__ == "__main__":
    scraper = ScraperHistorialMLB()
    scraper.extraer_y_guardar(dias_atras=30)  # empezar con 30 días
    scraper.cerrar()
