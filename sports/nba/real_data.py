import streamlit as st
import requests
from bs4 import BeautifulSoup

class NBARealData:
    # Extrae datos reales de NBA de TeamRankings.com
    # Basado en el exitoso proyecto nbabetinfo 
    
    def __init__(self):
        self.base_url = 'https://www.teamrankings.com/nba'
        self.ats_cache = {}
    
    def get_todays_games(self):
        # Obtiene partidos de HOY con spreads reales
        try:
            url = f'{self.base_url}'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraer partidos del sidebar
            games = []
            game_rows = soup.select('.matchup-row')
            
            for row in game_rows[:10]:
                teams = row.select('.team-name')
                if len(teams) >= 2:
                    home = teams[0].text.strip()
                    away = teams[1].text.strip()
                    
                    # Extraer spread
                    spread_elem = row.select('.spread')[0].text if row.select('.spread') else 'PK'
                    
                    games.append({
                        'home': home,
                        'away': away,
                        'spread': spread_elem,
                        'total': self._extract_total(row)
                    })
            return games
        except Exception as e:
            st.warning(f'Error cargando datos NBA: {e}')
            return self._get_mock_nba_games()
    
    def _extract_total(self, row):
        # Extrae total de puntos
        total_elem = row.select('.total')[0].text if row.select('.total') else '220'
        return total_elem
    
    def _get_mock_nba_games(self):
        # Fallback con datos reales de tu captura
        return [
            {'home': 'Memphis Grizzlies', 'away': 'Philadelphia 76ers', 
             'spread': '+3', 'total': '227.5'},
            {'home': 'Dallas Mavericks', 'away': 'Atlanta Hawks',
             'spread': '+9.5', 'total': '240'},
            {'home': 'Detroit Pistons', 'away': 'Brooklyn Nets',
             'spread': '-15.5', 'total': '217.5'},
            {'home': 'Washington Wizards', 'away': 'Miami Heat',
             'spread': '+15.5', 'total': '242.5'},
            {'home': 'Toronto Raptors', 'away': 'Houston Rockets',
             'spread': '+5', 'total': '217.5'},
        ]
