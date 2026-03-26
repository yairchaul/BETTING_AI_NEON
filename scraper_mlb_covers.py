# -*- coding: utf-8 -*-
"""
SCRAPER MLB - Extrae odds reales desde covers.com
No requiere API, solo scraping
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime

class ScraperMLBCovers:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_games(self):
        """Obtiene partidos MLB con odds reales"""
        url = "https://www.covers.com/sport/baseball/mlb/odds"
        
        try:
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            partidos = []
            
            # Buscar tabla de odds
            tabla = soup.find('table', class_=re.compile(r'odds-table|table-odds'))
            if not tabla:
                # Buscar por filas
                filas = soup.find_all('tr', class_=re.compile(r'odds-row|game-row'))
            else:
                filas = tabla.find_all('tr')
            
            for fila in filas:
                try:
                    # Extraer equipos
                    equipos = fila.find_all('span', class_=re.compile(r'team-name|team'))
                    if len(equipos) >= 2:
                        local = equipos[0].text.strip()
                        visitante = equipos[1].text.strip()
                    else:
                        continue
                    
                    # Extraer odds moneyline
                    odds_cells = fila.find_all('td', class_=re.compile(r'odds|moneyline'))
                    ml_local = "N/A"
                    ml_visit = "N/A"
                    
                    if len(odds_cells) >= 2:
                        ml_local = odds_cells[0].text.strip()
                        ml_visit = odds_cells[1].text.strip()
                    
                    # Extraer over/under
                    ou_cell = fila.find('td', class_=re.compile(r'total|over-under'))
                    over_under = 8.5
                    if ou_cell:
                        ou_text = ou_cell.text.strip()
                        nums = re.findall(r'\d+\.?\d*', ou_text)
                        if nums:
                            over_under = float(nums[0])
                    
                    partidos.append({
                        'local': local,
                        'visitante': visitante,
                        'fecha': datetime.now().strftime("%Y%m%d"),
                        'hora': '',
                        'lanzadores': '',
                        'odds': {
                            'over_under': over_under,
                            'moneyline': {'local': ml_local, 'visitante': ml_visit},
                            'spread': {'local': 'N/A', 'visitante': 'N/A'}
                        },
                        'records': {'local': '0-0', 'visitante': '0-0'}
                    })
                    
                except Exception as e:
                    continue
            
            print(f"⚾ MLB: {len(partidos)} partidos con odds desde covers.com")
            return partidos
            
        except Exception as e:
            print(f"Error scraping covers.com: {e}")
            return []

if __name__ == "__main__":
    scraper = ScraperMLBCovers()
    partidos = scraper.get_games()
    for p in partidos[:3]:
        print(f"{p['local']} vs {p['visitante']} | ML: {p['odds']['moneyline']} | OU: {p['odds']['over_under']}")
