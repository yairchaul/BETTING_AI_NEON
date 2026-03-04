# modules/odds_api_integrator.py
import requests
import streamlit as st
import time
import urllib3
from datetime import datetime

# Desactivar warnings de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class OddsAPIIntegrator:
    """
    Integraci?n con The Odds API (the-odds-api.com)
    Documentaci?n: https://the-odds-api.com
    """
    
    def __init__(self):
        self.api_key = st.secrets.get("ODDS_API_KEY", "")
        self.base_url = "https://api.the-odds-api.com/v4"
        self.last_request_time = 0
        self.request_interval = 0.25  # 4 requests por segundo
        
    def _rate_limit(self):
        """Controla el rate limiting"""
        now = time.time()
        time_since_last = now - self.last_request_time
        if time_since_last < self.request_interval:
            time.sleep(self.request_interval - time_since_last)
        self.last_request_time = time.time()
    
    def test_connection(self):
        """Prueba la conexi?n con la API"""
        if not self.api_key:
            return False, "? API Key no configurada"
        
        try:
            self._rate_limit()
            url = f"{self.base_url}/sports"
            params = {"apiKey": self.api_key}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                sports = response.json()
                return True, f"? Conexi?n exitosa! {len(sports)} deportes disponibles"
            else:
                return False, f"? Error {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"? Error de conexi?n: {e}"
    
    def get_sports(self):
        """Obtiene lista de todos los deportes disponibles"""
        if not self.api_key:
            return []
        
        try:
            self._rate_limit()
            url = f"{self.base_url}/sports"
            params = {"apiKey": self.api_key}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
        except:
            return []
    
    def get_upcoming_events(self, sport_key="soccer", regions="uk", markets="h2h"):
        """
        Obtiene eventos pr?ximos con odds
        """
        if not self.api_key:
            return []
        
        try:
            self._rate_limit()
            url = f"{self.base_url}/sports/{sport_key}/odds"
            params = {
                "apiKey": self.api_key,
                "regions": regions,
                "markets": markets,
                "oddsFormat": "decimal"
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error {response.status_code}: {response.text}")
                return []
        except Exception as e:
            print(f"Error obteniendo eventos: {e}")
            return []
    
    def get_events_today(self, country=None, league=None):
        """
        Obtiene eventos de f?tbol programados
        """
        eventos = self.get_upcoming_events(sport_key="soccer")
        
        # Filtrar por pa?s si se especifica
        if country and eventos:
            filtered = []
            country_lower = country.lower()
            for evento in eventos:
                # Buscar en los nombres de los equipos o en la liga
                home = evento.get('home_team', '').lower()
                away = evento.get('away_team', '').lower()
                
                # Palabras clave por pa?s
                if country_lower == "argentina":
                    keywords = ["argentinos", "boca", "river", "racing", "independiente", 
                               "san lorenzo", "lanus", "velez", "tigre", "platense"]
                    if any(keyword in home or keyword in away for keyword in keywords):
                        filtered.append(evento)
                elif country_lower == "spain" or country_lower == "espa?a":
                    keywords = ["real", "barcelona", "atletico", "valencia", "sevilla", 
                               "athletic", "sociedad", "betis"]
                    if any(keyword in home or keyword in away for keyword in keywords):
                        filtered.append(evento)
                else:
                    # Si no hay filtro, incluir todos
                    filtered.append(evento)
            return filtered
        
        return eventos
    
    def get_live_odds(self, home_team, away_team):
        """
        Busca odds para un partido espec?fico por nombres de equipos
        """
        if not self.api_key:
            return None
        
        try:
            # Obtener todos los eventos pr?ximos
            eventos = self.get_upcoming_events()
            
            # Buscar coincidencia
            for evento in eventos:
                event_home = evento.get('home_team', '').lower()
                event_away = evento.get('away_team', '').lower()
                
                home_lower = home_team.lower()
                away_lower = away_team.lower()
                
                # Verificar coincidencia (flexible)
                if (home_lower in event_home or event_home in home_lower) and \
                   (away_lower in event_away or event_away in away_lower):
                    
                    # Extraer odds de los bookmakers
                    bookmakers = evento.get('bookmakers', [])
                    mejores_odds = self._get_best_odds(bookmakers)
                    
                    if mejores_odds:
                        return {
                            'partido': f"{evento.get('home_team')} vs {evento.get('away_team')}",
                            'cuota_local': mejores_odds['home'],
                            'cuota_empate': mejores_odds['draw'],
                            'cuota_visitante': mejores_odds['away'],
                            'liga': 'Primera Divisi?n Argentina',  # Por ahora fijo
                            'fecha': evento.get('commence_time', ''),
                            'bookmaker': 'M?ltiples'
                        }
            
            return None
            
        except Exception as e:
            print(f"Error en get_live_odds: {e}")
            return None
    
    def _get_best_odds(self, bookmakers):
        """
        Encuentra las mejores odds entre todos los bookmakers
        """
        try:
            best = {'home': 0, 'draw': 0, 'away': 0}
            
            for bookmaker in bookmakers:
                markets = bookmaker.get('markets', [])
                for market in markets:
                    if market.get('key') == 'h2h':
                        outcomes = market.get('outcomes', [])
                        for outcome in outcomes:
                            name = outcome.get('name', '').lower()
                            price = outcome.get('price', 0)
                            
                            if 'home' in name or name == bookmaker.get('home_team', '').lower():
                                best['home'] = max(best['home'], price)
                            elif 'away' in name or name == bookmaker.get('away_team', '').lower():
                                best['away'] = max(best['away'], price)
                            elif 'draw' in name:
                                best['draw'] = max(best['draw'], price)
            
            if best['home'] > 0 and best['draw'] > 0 and best['away'] > 0:
                return best
        except:
            pass
        return None
    
    def find_value_bets(self, partidos_analizados, umbral_ev=0.05):
        """
        Encuentra value bets comparando nuestras probabilidades con odds reales
        """
        value_bets = []
        
        for analisis in partidos_analizados:
            home_team = analisis.get('home_team', '')
            away_team = analisis.get('away_team', '')
            
            if not home_team or not away_team:
                continue
            
            odds_reales = self.get_live_odds(home_team, away_team)
            
            if odds_reales:
                probs = analisis.get('final_probs', [0.33, 0.34, 0.33])
                
                mercados = [
                    ('Gana Local', probs[0] if len(probs) > 0 else 0.33, odds_reales['cuota_local']),
                    ('Empate', probs[1] if len(probs) > 1 else 0.34, odds_reales['cuota_empate']),
                    ('Gana Visitante', probs[2] if len(probs) > 2 else 0.33, odds_reales['cuota_visitante'])
                ]
                
                for mercado, prob, odd in mercados:
                    if odd and prob and odd > 1.0:
                        ev = (prob * odd) - 1
                        if ev > umbral_ev:
                            value_bets.append({
                                'partido': f"{home_team} vs {away_team}",
                                'liga': analisis.get('league', 'Desconocida'),
                                'mercado': mercado,
                                'probabilidad': round(prob * 100, 2),
                                'odd_real': odd,
                                'ev': round(ev * 100, 2),
                                'confianza': '?? ALTA' if ev > 0.10 else '?? MEDIA',
                                'kelly_sugerido': self._calcular_kelly(prob, odd)
                            })
        
        return sorted(value_bets, key=lambda x: x['ev'], reverse=True)
    
    def _calcular_kelly(self, prob, odd):
        """Calcula fracci?n de Kelly"""
        b = odd - 1
        p = prob
        q = 1 - p
        
        if b <= 0:
            return 0
        
        kelly = (b * p - q) / b
        return round(max(0, min(kelly * 0.25, 0.05)) * 100, 2)
