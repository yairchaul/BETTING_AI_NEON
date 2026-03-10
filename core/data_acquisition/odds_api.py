import streamlit as st
from odds_api import OddsAPIClient

class OddsAPIClientWrapper:
    # Cliente para conectarse a Odds-API.io
    
    def __init__(self):
        self.api_key = st.secrets.get('ODDS_API_KEY', '98ccdb7d4c28042caa8bc8fe7ff6cc62')
        self.client = OddsAPIClient(api_key=self.api_key)
    
    def get_soccer_events_mx(self):
        # Obtiene eventos de fútbol en México (Caliente.mx)
        try:
            # Según la documentación de the-odds-api-sdk [citation:2]
            # El parámetro correcto es 'regions' como lista
            events = self.client.get_events(
                sport='soccer', 
                regions=['mx', 'us']
            )
            return self._parse_events(events)
        except TypeError as e:
            # Si falla con 'regions', probar con 'region' (singular)
            try:
                st.warning("Intentando con parámetro 'region'...")
                events = self.client.get_events(
                    sport='soccer', 
                    region='mx'
                )
                return self._parse_events(events)
            except Exception as e2:
                st.error(f'Error conectando a Odds-API: {e2}')
                return []
        except Exception as e:
            st.error(f'Error conectando a Odds-API: {e}')
            return []
    
    def _parse_events(self, events):
        # Parsea los eventos al formato del sistema
        parsed = []
        if not events:
            return parsed
            
        for event in events[:10]:  # Límite para no saturar
            home = getattr(event, 'home_team', 'Local') if not isinstance(event, dict) else event.get('home_team', 'Local')
            away = getattr(event, 'away_team', 'Visitante') if not isinstance(event, dict) else event.get('away_team', 'Visitante')
            
            parsed.append({
                'deporte': '⚽ Fútbol',
                'liga': getattr(event, 'sport_title', 'Liga') if not isinstance(event, dict) else event.get('sport_title', 'Liga'),
                'local': home,
                'visitante': away,
                'odds': {
                    'local': 2.0,
                    'empate': 3.5,
                    'visitante': 2.5
                }
            })
        return parsed
    
    def close(self):
        self.client.close()
