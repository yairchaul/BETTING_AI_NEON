# -*- coding: utf-8 -*-
"""
SCRAPER ODDS UFC - Desde covers.com (alternativa estable)
Extrae odds en formato americano (+525, -900)
"""

import requests
from bs4 import BeautifulSoup
import re

class ScraperOddsCovers:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
    
    def obtener_odds_ufc(self):
        """Obtiene odds de UFC desde covers.com"""
        url = "https://www.covers.com/sport/mma/ufc/odds"
        
        try:
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            odds = {}
            
            # Buscar en la tabla de odds
            tablas = soup.find_all('table')
            
            for tabla in tablas:
                filas = tabla.find_all('tr')
                for fila in filas:
                    celdas = fila.find_all('td')
                    if len(celdas) >= 2:
                        # Extraer nombres y odds
                        nombres = []
                        odds_list = []
                        
                        for celda in celdas:
                            texto = celda.get_text().strip()
                            # Si es un nombre (solo letras y espacios)
                            if re.match(r'^[A-Za-z\s]+$', texto) and len(texto) > 2:
                                nombres.append(texto)
                            # Si es un odd (+123 o -123)
                            elif re.match(r'^[+-]\d+$', texto):
                                odds_list.append(texto)
                        
                        # Asignar odds a nombres
                        for i, nombre in enumerate(nombres):
                            if i < len(odds_list):
                                odds[nombre.lower()] = odds_list[i]
            
            # También buscar en divs específicos
            peleadores = soup.find_all('div', class_=re.compile(r'fighter|competitor|participant'))
            for p in peleadores:
                nombre_elem = p.find('span', class_=re.compile(r'name|fighter-name'))
                odd_elem = p.find('span', class_=re.compile(r'odds|price'))
                if nombre_elem and odd_elem:
                    nombre = nombre_elem.text.strip()
                    odd = odd_elem.text.strip()
                    if odd.startswith('+') or odd.startswith('-'):
                        odds[nombre.lower()] = odd
            
            return odds
            
        except Exception as e:
            print(f"Error obteniendo odds: {e}")
            return {}
    
    def obtener_odds_para_peleadores(self, peleadores):
        """Obtiene odds específicas para una lista de peleadores"""
        odds_todas = self.obtener_odds_ufc()
        
        resultados = {}
        for peleador in peleadores:
            nombre_lower = peleador.lower()
            for key, value in odds_todas.items():
                if nombre_lower in key or key in nombre_lower:
                    resultados[peleador] = value
                    break
        
        return resultados

if __name__ == "__main__":
    scraper = ScraperOddsCovers()
    odds = scraper.obtener_odds_ufc()
    
    print("\n📊 Odds encontradas (covers.com):")
    for nombre, odd in list(odds.items())[:30]:
        print(f"   {nombre}: {odd}")
