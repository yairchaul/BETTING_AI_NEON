# -*- coding: utf-8 -*-
"""
SCRAPER FÚTBOL - Extrae resultados reales desde soccerway.com
Para llenar BD con datos históricos
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime, timedelta

class ScraperFutbolSoccerway:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def obtener_resultados_liga(self, liga_url, dias_atras=30):
        """Obtiene resultados de una liga específica"""
        url = f"https://int.soccerway.com{liga_url}"
        
        try:
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            partidos = []
            
            # Buscar tabla de resultados
            tabla = soup.find('table', class_='matches')
            if not tabla:
                return []
            
            filas = tabla.find_all('tr', class_='match')
            
            for fila in filas:
                try:
                    # Equipos
                    equipos = fila.find_all('td', class_='team')
                    if len(equipos) >= 2:
                        local = equipos[0].text.strip()
                        visitante = equipos[1].text.strip()
                    else:
                        continue
                    
                    # Marcador
                    score_cell = fila.find('td', class_='score')
                    if score_cell:
                        score_text = score_cell.text.strip()
                        nums = re.findall(r'\d+', score_text)
                        if len(nums) >= 2:
                            goles_local = int(nums[0])
                            goles_visit = int(nums[1])
                        else:
                            continue
                    else:
                        continue
                    
                    # Fecha
                    fecha_cell = fila.find('td', class_='date')
                    if fecha_cell:
                        fecha_text = fecha_cell.text.strip()
                        # Parsear fecha (formato: "26.03.2026")
                        try:
                            fecha = datetime.strptime(fecha_text, "%d.%m.%Y").strftime("%Y%m%d")
                        except:
                            fecha = datetime.now().strftime("%Y%m%d")
                    else:
                        fecha = datetime.now().strftime("%Y%m%d")
                    
                    partidos.append({
                        'local': local,
                        'visitante': visitante,
                        'goles_local': goles_local,
                        'goles_visitante': goles_visit,
                        'fecha': fecha
                    })
                    
                except Exception as e:
                    continue
            
            return partidos
            
        except Exception as e:
            print(f"Error scraping soccerway: {e}")
            return []
    
    def guardar_en_bd(self, partidos):
        """Guarda resultados en BD"""
        import sqlite3
        
        conn = sqlite3.connect("data/betting_stats.db")
        cursor = conn.cursor()
        
        for p in partidos:
            cursor.execute('''
                INSERT OR IGNORE INTO historial_equipos 
                (nombre_equipo, deporte, puntos_favor, puntos_contra, fecha, temporada)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (p['local'], 'futbol', p['goles_local'], p['goles_visitante'], p['fecha'], "2026"))
            
            cursor.execute('''
                INSERT OR IGNORE INTO historial_equipos 
                (nombre_equipo, deporte, puntos_favor, puntos_contra, fecha, temporada)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (p['visitante'], 'futbol', p['goles_visitante'], p['goles_local'], p['fecha'], "2026"))
        
        conn.commit()
        conn.close()
        print(f"✅ Guardados {len(partidos)} partidos en BD")

# Ligas populares en soccerway
LIGAS_SOCCERWAY = {
    "Premier League": "/national/england/premier-league/",
    "La Liga": "/national/spain/primera-division/",
    "Serie A": "/national/italy/serie-a/",
    "Bundesliga": "/national/germany/bundesliga/",
    "Ligue 1": "/national/france/ligue-1/",
    "Liga MX": "/national/mexico/primera-division/",
    "Argentine Primera": "/national/argentina/primera-division/"
}

if __name__ == "__main__":
    scraper = ScraperFutbolSoccerway()
    
    for nombre, url in LIGAS_SOCCERWAY.items():
        print(f"\n📡 Scrapeando {nombre}...")
        partidos = scraper.obtener_resultados_liga(url, dias_atras=30)
        if partidos:
            scraper.guardar_en_bd(partidos)
        time.sleep(2)
