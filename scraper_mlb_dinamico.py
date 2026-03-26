# -*- coding: utf-8 -*-
"""
SCRAPER MLB DINÁMICO - Extrae odds reales desde covers.com
Funciona para los partidos del día actual
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

class ScraperMLBDinamico:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-MX,es;q=0.9',
        })
    
    def get_games(self):
        """Obtiene partidos MLB del día actual"""
        url = "https://www.covers.com/sport/baseball/mlb/odds"
        
        try:
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            partidos = []
            
            # Buscar TODAS las filas que contienen equipos
            # Método 1: Buscar por clase game-row
            filas = soup.find_all('tr', class_=re.compile(r'game-row|odds-row|row'))
            
            # Método 2: Si no encuentra, buscar por estructura de tabla
            if not filas:
                tablas = soup.find_all('table')
                for tabla in tablas:
                    filas_tabla = tabla.find_all('tr')
                    for fila in filas_tabla:
                        if fila.find_all('td', class_=re.compile(r'team|odds')):
                            filas.append(fila)
            
            for fila in filas:
                try:
                    # Buscar nombres de equipos (pueden estar en diferentes etiquetas)
                    equipos = fila.find_all(['span', 'td'], class_=re.compile(r'team-name|team'))
                    
                    # Si no encuentra por clase, buscar por texto que parezca equipo
                    if len(equipos) < 2:
                        celdas = fila.find_all('td')
                        textos = [celda.text.strip() for celda in celdas if celda.text.strip()]
                        # Filtrar solo nombres (sin números)
                        equipos_texto = [t for t in textos if not t.replace('-', '').replace('+', '').replace('.', '').isdigit()]
                        if len(equipos_texto) >= 2:
                            local = equipos_texto[0]
                            visitante = equipos_texto[1]
                        else:
                            continue
                    else:
                        local = equipos[0].text.strip()
                        visitante = equipos[1].text.strip()
                    
                    # Buscar odds
                    odds_celdas = fila.find_all(['td', 'span'], class_=re.compile(r'odds|moneyline'))
                    ml_local = "N/A"
                    ml_visit = "N/A"
                    
                    odds_textos = []
                    for oc in odds_celdas:
                        texto = oc.text.strip()
                        if texto and (texto.startswith('+') or texto.startswith('-') or texto.isdigit()):
                            odds_textos.append(texto)
                    
                    if len(odds_textos) >= 2:
                        ml_local = odds_textos[0]
                        ml_visit = odds_textos[1]
                    
                    # Buscar total (Over/Under)
                    total_celdas = fila.find_all(['td', 'span'], class_=re.compile(r'total|over-under'))
                    over_under = 8.5
                    for tc in total_celdas:
                        texto = tc.text.strip()
                        nums = re.findall(r'\d+\.?\d*', texto)
                        if nums:
                            over_under = float(nums[0])
                            break
                    
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
    scraper = ScraperMLBDinamico()
    partidos = scraper.get_games()
    for p in partidos[:5]:
        print(f"{p['local']} vs {p['visitante']} | ML: {p['odds']['moneyline']} | OU: {p['odds']['over_under']}")
