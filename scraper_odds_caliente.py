# -*- coding: utf-8 -*-
"""
SCRAPER ODDS UFC - Desde Caliente.mx
Extrae odds reales de la casa de apuestas mexicana
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
from datetime import datetime

class ScraperOddsCaliente:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-MX,es;q=0.9,en;q=0.8',
            'Referer': 'https://www.caliente.mx/',
        })
    
    def obtener_odds_ufc(self, evento="ufc-fight-night-adesanya-vs-pyfer"):
        """Obtiene odds de UFC desde Caliente.mx"""
        url = f"https://www.caliente.mx/es/mx/ufc-mma/{evento}"
        
        print(f"📡 Extrayendo odds desde Caliente.mx...")
        
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                print(f"⚠️ Error HTTP {response.status_code}")
                return {}
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            odds = {}
            
            # Método 1: Buscar en la estructura de la página
            # Buscar contenedores de peleadores
            peleadores = soup.find_all('div', class_=re.compile(r'participant|fighter|competitor'))
            
            for p in peleadores:
                nombre_elem = p.find('span', class_=re.compile(r'name|participant-name'))
                odd_elem = p.find('span', class_=re.compile(r'odd|price|value'))
                
                if nombre_elem and odd_elem:
                    nombre = nombre_elem.text.strip()
                    odd = odd_elem.text.strip()
                    if odd.startswith('+') or odd.startswith('-'):
                        odds[nombre.lower()] = odd
            
            # Método 2: Buscar en el JSON incrustado
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'window.__INITIAL_STATE__' in script.string:
                    try:
                        # Extraer JSON
                        json_text = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', script.string, re.DOTALL)
                        if json_text:
                            data = json.loads(json_text.group(1))
                            # Navegar hasta encontrar odds
                            if 'events' in data:
                                for event in data['events']:
                                    if 'participants' in event:
                                        for p in event['participants']:
                                            nombre = p.get('name', '')
                                            odd = p.get('odds', {}).get('american', '')
                                            if nombre and odd:
                                                odds[nombre.lower()] = odd
                    except:
                        pass
            
            print(f"✅ Encontrados {len(odds)} odds")
            return odds
            
        except Exception as e:
            print(f"❌ Error extrayendo odds: {e}")
            return {}
    
    def obtener_odds_por_peleador(self, nombre_peleador):
        """Busca odds específicas para un peleador"""
        odds = self.obtener_odds_ufc()
        nombre_lower = nombre_peleador.lower()
        
        for key, value in odds.items():
            if nombre_lower in key or key in nombre_lower:
                return value
        
        return None

def obtener_odds_para_cartelera(cartelera):
    """Obtiene odds para todos los peleadores de una cartelera"""
    scraper = ScraperOddsCaliente()
    odds = scraper.obtener_odds_ufc()
    
    resultados = {}
    for pelea in cartelera:
        p1 = pelea.get('peleador1', '')
        p2 = pelea.get('peleador2', '')
        
        odd1 = None
        odd2 = None
        
        for key, value in odds.items():
            if p1.lower() in key or key in p1.lower():
                odd1 = value
            if p2.lower() in key or key in p2.lower():
                odd2 = value
        
        resultados[p1] = odd1
        resultados[p2] = odd2
        
        print(f"   {p1}: {odd1 if odd1 else 'N/A'} | {p2}: {odd2 if odd2 else 'N/A'}")
    
    return resultados

if __name__ == "__main__":
    scraper = ScraperOddsCaliente()
    odds = scraper.obtener_odds_ufc()
    
    print("\n📊 Odds encontradas:")
    for nombre, odd in list(odds.items())[:20]:
        print(f"   {nombre}: {odd}")
