# modules/odds_api_integrator.py
import requests
import streamlit as st
import pandas as pd
from datetime import datetime
import time

class OddsAPIIntegrator:
    """
    Integración profesional con Odds-API.io para Windows usando requests
    """
    
    def __init__(self):
        self.api_key = st.secrets.get("ODDS_API_KEY", "")
        self.base_url = "https://api.oddsapi.io"
        self.last_request_time = 0
        self.request_interval = 0.25  # 4 requests por segundo (respetar rate limit)
        
    def _rate_limit(self):
        """Controla el rate limiting"""
        now = time.time()
        time_since_last = now - self.last_request_time
        if time_since_last < self.request_interval:
            time.sleep(self.request_interval - time_since_last)
        self.last_request_time = time.time()
    
    def get_live_odds(self, home_team, away_team):
        """
        Obtiene odds EN VIVO para un partido específico
        """
        if not self.api_key:
            st.warning("⚠️ ODDS_API_KEY no configurada en secrets.toml")
            return None
        
        try:
            self._rate_limit()
            
            # Buscar partidos por equipo
            search_url = f"{self.base_url}/v1/events"
            params = {
                "apiKey": self.api_key,
                "sport": "soccer",
                "name": f"{home_team} {away_team}",
                "status": "live,upcoming"
            }
            
            response = requests.get(search_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('events') and len(data['events']) > 0:
                    event = data['events'][0]
                    event_id = event['id']
                    
                    # Obtener odds del evento
                    odds_url = f"{self.base_url}/v1/events/{event_id}/odds"
                    odds_params = {
                        "apiKey": self.api_key,
                        "bookmakers": "pinnacle,bet365,caliente",
                        "markets": "h2h"  # Head to head (1X2)
                    }
                    
                    odds_response = requests.get(odds_url, params=odds_params)
                    
                    if odds_response.status_code == 200:
                        odds_data = odds_response.json()
                        
                        return {
                            'partido': f"{home_team} vs {away_team}",
                            'cuota_local': self._extract_odds(odds_data, 'home'),
                            'cuota_empate': self._extract_odds(odds_data, 'draw'),
                            'cuota_visitante': self._extract_odds(odds_data, 'away'),
                            'liga': event.get('league', 'Desconocida'),
                            'fecha': event.get('start_time', ''),
                            'bookmaker': 'Pinnacle/Bet365'
                        }
            
            return None
            
        except Exception as e:
            st.error(f"Error obteniendo odds: {e}")
            return None
    
    def _extract_odds(self, odds_data, market_type):
        """Extrae odds específicas del mercado"""
        try:
            market_map = {
                'home': 0,  # Índice para local
                'draw': 1,  # Índice para empate
                'away': 2   # Índice para visitante
            }
            
            if odds_data.get('odds'):
                for bookmaker in odds_data['odds']:
                    if bookmaker.get('markets'):
                        for market in bookmaker['markets']:
                            if market.get('key') == 'h2h':
                                outcomes = market.get('outcomes', [])
                                if len(outcomes) > market_map[market_type]:
                                    return float(outcomes[market_map[market_type]])
        except:
            pass
        return None
    
    def find_value_bets(self, partidos_analizados, umbral_ev=0.05):
        """
        Compara nuestras probabilidades con odds reales del mercado
        """
        value_bets = []
        
        for analisis in partidos_analizados:
            # Extraer equipos del análisis
            home_team = analisis.get('home_team', '')
            away_team = analisis.get('away_team', '')
            
            if not home_team or not away_team:
                continue
            
            odds_reales = self.get_live_odds(home_team, away_team)
            
            if odds_reales:
                # Obtener probabilidades del análisis
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
                                'confianza': '🚀 ALTA' if ev > 0.10 else '📊 MEDIA',
                                'kelly_sugerido': self._calcular_kelly(prob, odd)
                            })
        
        return sorted(value_bets, key=lambda x: x['ev'], reverse=True)
    
    def _calcular_kelly(self, prob, odd):
        """Calcula fracción de Kelly"""
        b = odd - 1
        p = prob
        q = 1 - p
        
        if b <= 0:
            return 0
        
        kelly = (b * p - q) / b
        return round(max(0, min(kelly * 0.25, 0.05)) * 100, 2)  # 25% de Kelly, max 5% del bank
    
    def test_connection(self):
        """Prueba la conexión con la API"""
        if not self.api_key:
            return False, "❌ API Key no configurada"
        
        try:
            self._rate_limit()
            test_url = f"{self.base_url}/v1/sports"
            params = {"apiKey": self.api_key}
            
            response = requests.get(test_url, params=params)
            
            if response.status_code == 200:
                return True, "✅ Conexión exitosa con Odds-API.io"
            else:
                return False, f"❌ Error {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"❌ Error de conexión: {e}"
