import streamlit as st
import requests
import json
from datetime import datetime
import time

class ESPNScraper:
    # Scraper para obtener datos reales de UFC desde ESPN
    
    def __init__(self):
        self.base_url = "https://www.espn.com.mx/mma/fightcenter"
        self.api_base = "http://site.api.espn.com/apis/site/v2/sports/mma/ufc"
        self.cache = {}
        self.session = requests.Session()
        # Headers para simular un navegador real [citation:7]
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def get_upcoming_events(self):
        # Obtiene los próximos eventos de UFC
        try:
            # ESPN tiene un endpoint público para eventos [citation:1]
            url = f"{self.api_base}/events"
            response = self.session.get(url, params={'limit': 10})
            
            if response.status_code == 200:
                data = response.json()
                events = []
                for event in data.get('events', []):
                    events.append({
                        'id': event.get('id'),
                        'name': event.get('name'),
                        'date': event.get('date'),
                        'venue': event.get('venue', {}).get('name', ''),
                        'city': event.get('venue', {}).get('city', ''),
                        'state': event.get('venue', {}).get('state', ''),
                        'fights': self._parse_fights(event.get('competitions', []))
                    })
                return events
            else:
                st.warning(f"Error {response.status_code} al obtener eventos")
                return self._get_fallback_events()
        except Exception as e:
            st.warning(f"Error conectando a ESPN: {e}")
            return self._get_fallback_events()
    
    def get_fight_details(self, event_id):
        # Obtiene detalles de todas las peleas de un evento
        try:
            url = f"{self.api_base}/events/{event_id}/competitions"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_fights(data.get('items', []))
            return []
        except Exception as e:
            st.warning(f"Error obteniendo peleas: {e}")
            return []
    
    def _parse_fights(self, competitions):
        # Parsea las peleas al formato de nuestro modelo
        fights = []
        
        for comp in competitions:
            competitors = comp.get('competitors', [])
            if len(competitors) >= 2:
                f1 = competitors[0]
                f2 = competitors[1]
                
                # Extraer estadísticas de los peleadores [citation:2]
                fight = {
                    'fighter1': {
                        'name': f1.get('athlete', {}).get('displayName', ''),
                        'record': f1.get('record', ''),
                        'odds': self._extract_odds(comp, f1.get('athlete', {}).get('displayName', '')),
                        'stats': self._get_fighter_stats(f1.get('athlete', {}).get('id')),
                        'country': f1.get('athlete', {}).get('birthPlace', {}).get('country', ''),
                        'height': self._parse_height(f1.get('athlete', {}).get('displayHeight', '')),
                        'weight': self._parse_weight(f1.get('athlete', {}).get('displayWeight', '')),
                        'age': self._calculate_age(f1.get('athlete', {}).get('birthDate')),
                        'reach': f1.get('athlete', {}).get('reach', 0),
                        'stance': f1.get('athlete', {}).get('stance', '')
                    },
                    'fighter2': {
                        'name': f2.get('athlete', {}).get('displayName', ''),
                        'record': f2.get('record', ''),
                        'odds': self._extract_odds(comp, f2.get('athlete', {}).get('displayName', '')),
                        'stats': self._get_fighter_stats(f2.get('athlete', {}).get('id')),
                        'country': f2.get('athlete', {}).get('birthPlace', {}).get('country', ''),
                        'height': self._parse_height(f2.get('athlete', {}).get('displayHeight', '')),
                        'weight': self._parse_weight(f2.get('athlete', {}).get('displayWeight', '')),
                        'age': self._calculate_age(f2.get('athlete', {}).get('birthDate')),
                        'reach': f2.get('athlete', {}).get('reach', 0),
                        'stance': f2.get('athlete', {}).get('stance', '')
                    },
                    'weight_class': comp.get('weightClass', ''),
                    'rounds': comp.get('rounds', 3),
                    'status': comp.get('status', {}).get('type', {}).get('description', '')
                }
                fights.append(fight)
        
        return fights
    
    def _get_fighter_stats(self, athlete_id):
        # Obtiene estadísticas detalladas de un peleador
        if not athlete_id:
            return {}
        
        try:
            # Endpoint de estadísticas de ESPN [citation:1]
            url = f"https://site.web.api.espn.com/apis/common/v3/sports/mma/ufc/athletes/{athlete_id}/stats"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                categories = data.get('categories', [])
                
                stats = {
                    'significant_strikes_landed': 0,
                    'significant_strikes_attempted': 0,
                    'takedowns_landed': 0,
                    'takedowns_attempted': 0,
                    'submissions_avg': 0,
                    'knockouts': 0,
                    'submissions': 0,
                    'decisions': 0
                }
                
                # Procesar estadísticas [citation:2]
                for cat in categories:
                    if cat.get('displayName') == 'Striking':
                        for stat in cat.get('stats', []):
                            if 'significantStrikesLanded' in stat.get('name', ''):
                                stats['significant_strikes_landed'] = float(stat.get('value', 0))
                            if 'significantStrikesAttempted' in stat.get('name', ''):
                                stats['significant_strikes_attempted'] = float(stat.get('value', 0))
                    
                    elif cat.get('displayName') == 'Wrestling':
                        for stat in cat.get('stats', []):
                            if 'takedownsLanded' in stat.get('name', ''):
                                stats['takedowns_landed'] = float(stat.get('value', 0))
                            if 'takedownsAttempted' in stat.get('name', ''):
                                stats['takedowns_attempted'] = float(stat.get('value', 0))
                
                return stats
        except Exception as e:
            pass
        return {}
    
    def _extract_odds(self, competition, fighter_name):
        # Extrae odds de la competencia (si están disponibles)
        try:
            odds_data = competition.get('odds', [])
            for odd in odds_data:
                if odd.get('name') == fighter_name:
                    return odd.get('american', '+100')
        except:
            pass
        return '+100'
    
    def _parse_height(self, height_str):
        # Convierte altura (ej. "6'4\"") a cm
        try:
            if height_str and "'" in height_str:
                feet, inches = height_str.replace('"', '').split("'")
                return int(float(feet) * 30.48 + float(inches) * 2.54)
        except:
            pass
        return 175
    
    def _parse_weight(self, weight_str):
        # Convierte peso (ej. "248 lbs") a kg
        try:
            if weight_str and 'lbs' in weight_str:
                lbs = weight_str.replace(' lbs', '').strip()
                return int(float(lbs) * 0.453592)
        except:
            return 84
    
    def _calculate_age(self, birth_date):
        # Calcula edad desde timestamp o string
        if not birth_date:
            return 30
        try:
            if isinstance(birth_date, int):
                from datetime import datetime
                birth_year = datetime.fromtimestamp(birth_date/1000).year
                current_year = datetime.now().year
                return current_year - birth_year
        except:
            pass
        return 30
    
    def _get_fallback_events(self):
        # Datos de respaldo en caso de que la API falle
        return [
            {
                'name': 'UFC Fight Night: Emmett vs. Vallejos',
                'date': '2026-03-15',
                'venue': 'Meta APEX, Las Vegas, NV',
                'fights': [
                    {
                        'fighter1': {'name': 'Josh Emmett', 'record': '19-6-0', 'odds': -163},
                        'fighter2': {'name': 'Kevin Vallejos', 'record': '17-1-0', 'odds': +125},
                        'weight_class': 'Peso Pluma',
                        'rounds': 5
                    },
                    {
                        'fighter1': {'name': 'Amanda Lemos', 'record': '15-5-1', 'odds': -550},
                        'fighter2': {'name': 'Gillian Robertson', 'record': '16-8-0', 'odds': +375},
                        'weight_class': 'Peso Paja',
                        'rounds': 3
                    },
                    {
                        'fighter1': {'name': 'Ion Cutelaba', 'record': '19-11-1', 'odds': -209},
                        'fighter2': {'name': 'Oumar Sy', 'record': '12-1-0', 'odds': +165},
                        'weight_class': 'Peso Semi-Pesado',
                        'rounds': 3
                    },
                    {
                        'fighter1': {'name': 'Andre Fili', 'record': '25-12-0', 'odds': -223},
                        'fighter2': {'name': 'Jose Delgado', 'record': '10-2-0', 'odds': +170},
                        'weight_class': 'Peso Pluma',
                        'rounds': 3
                    },
                    {
                        'fighter1': {'name': 'Brad Tavares', 'record': '21-12-0', 'odds': -143},
                        'fighter2': {'name': 'Eryk Anders', 'record': '17-9-0', 'odds': +110},
                        'weight_class': 'Peso Mediano',
                        'rounds': 3
                    }
                ]
            }
        ]

# Para pruebas rápidas
if __name__ == '__main__':
    scraper = ESPNScraper()
    events = scraper.get_upcoming_events()
    print(f"Eventos encontrados: {len(events)}")
