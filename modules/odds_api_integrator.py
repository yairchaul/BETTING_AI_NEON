# modules/odds_api_integrator.py
from odds_api import OddsAPIClient
import streamlit as st

class OddsAPIIntegrator:
    def __init__(self):
        self.api_key = st.secrets.get("ODDS_API_KEY", "")
        self.client = None
        if self.api_key:
            self.client = OddsAPIClient(api_key=self.api_key)
    
    def get_real_odds(self, home_team, away_team):
        """Obtiene odds reales de múltiples bookmakers"""
        if not self.client:
            return None
        
        try:
            # Buscar eventos que coincidan
            events = self.client.search_events(query=f"{home_team} {away_team}")
            
            if events:
                # Obtener odds del primer evento
                event_id = events[0]['id']
                odds = self.client.get_event_odds(event_id, bookmakers="pinnacle,bet365")
                return odds
        except:
            return None
        return None
    
    def find_value_bets(self, our_probability, market_odds):
        """Compara nuestra probabilidad con las odds del mercado"""
        # Si nuestra probabilidad > probabilidad implícita de la cuota -> VALUE!
        pass
