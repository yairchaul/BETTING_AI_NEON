import streamlit as st
import pandas as pd
from .models import NBAModelEV
from .rules import NBARules

class NBAProcessor:
    # Procesador específico para NBA con análisis de Handicap, Totales y Moneyline
    
    def __init__(self):
        self.model = NBAModelEV()
        self.rules = NBARules()
    
    def parse_nba_captura(self, line):
        # Parsea una línea de captura de NBA
        # Formato: "Equipo Spread Odds O/U Total Odds Moneyline"
        # Ejemplo: "Memphis Grizzlies+3-110O 227.5-112+130"
        import re
        
        # Buscar el equipo (todo hasta que aparezca + o -)
        equipo = re.match(r'^([A-Za-z\s]+?)(?=[+-])', line)
        if not equipo:
            return None
        equipo = equipo.group(1).strip()
        resto = line[len(equipo):]
        
        # Extraer spread
        spread_match = re.match(r'^([+-]\d+\.?\d*)', resto)
        if not spread_match:
            return None
        spread = spread_match.group(1)
        resto = resto[len(spread):]
        
        # Extraer odds del spread
        odds_spread_match = re.match(r'^([+-]?\d+)', resto)
        if not odds_spread_match:
            return None
        odds_spread = odds_spread_match.group(1)
        resto = resto[len(odds_spread):]
        
        # Extraer O/U
        ou_match = re.match(r'^([OU])', resto)
        if not ou_match:
            return None
        ou = ou_match.group(1)
        resto = resto[1:]
        
        # Extraer total
        total_match = re.match(r'^(\d+\.?\d*)', resto)
        if not total_match:
            return None
        total = total_match.group(1)
        resto = resto[len(total):]
        
        # Extraer odds del total
        odds_total_match = re.match(r'^([+-]?\d+)', resto)
        if not odds_total_match:
            return None
        odds_total = odds_total_match.group(1)
        resto = resto[len(odds_total):]
        
        # El resto es moneyline
        moneyline = resto
        
        return {
            'equipo': equipo,
            'spread': spread,
            'odds_spread': odds_spread,
            'ou': ou,
            'total': total,
            'odds_total': odds_total,
            'moneyline': moneyline
        }
    
    def parse_games(self, lines):
        # Parsea múltiples líneas en juegos (cada juego tiene 2 líneas)
        games = []
        i = 0
        while i < len(lines) - 1:
            home_data = self.parse_nba_captura(lines[i])
            away_data = self.parse_nba_captura(lines[i+1])
            if home_data and away_data:
                games.append({
                    'home': home_data['equipo'],
                    'away': away_data['equipo'],
                    'spread': home_data['spread'],
                    'total': home_data['total'],
                    'odds_home_spread': home_data['odds_spread'],
                    'odds_away_spread': away_data['odds_spread'],
                    'ou_home': home_data['ou'],
                    'ou_away': away_data['ou'],
                    'odds_home_total': home_data['odds_total'],
                    'odds_away_total': away_data['odds_total'],
                    'moneyline_home': home_data['moneyline'],
                    'moneyline_away': away_data['moneyline']
                })
            i += 2
        return games
    
    def render_game(self, idx, game):
        # Renderiza un juego NBA en la UI
        with st.expander(f"**🏀 {game['home']} vs {game['away']}**", expanded=(idx == 0)):
            # Mostrar datos crudos de la captura
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"### 🏠 **{game['home']}**")
                st.metric("Spread", game['spread'], game['odds_home_spread'])
                st.metric("Moneyline", game['moneyline_home'])
            with col2:
                st.markdown(f"### 🚀 **{game['away']}**")
                st.metric("Spread", game['spread'], game['odds_away_spread'])
                st.metric("Moneyline", game['moneyline_away'])
            with col3:
                st.markdown("### 📊 Totales")
                st.metric("Total", game['total'])
                st.metric("Over Odds", game['odds_home_total'])
                st.metric("Under Odds", game['odds_away_total'])
            with col4:
                st.markdown("### 🔍 O/U")
                st.metric("Casa", f"O {game['total']}", game['odds_home_total'])
                st.metric("Visitante", f"U {game['total']}", game['odds_away_total'])
            
            # Calcular probabilidades con modelo NBA
            analysis = self.model.calculate_game_probabilities(
                game['home'], game['away'],
                float(game['spread']), float(game['total']),
                game['odds_home_spread'], game['odds_away_spread'],
                game['moneyline_home'], game['moneyline_away']
            )
            
            # Mostrar análisis
            st.subheader("📊 Análisis Predictivo")
            col_a1, col_a2, col_a3 = st.columns(3)
            with col_a1:
                st.metric(
                    "Spread Esperado",
                    f"{analysis['spread_analysis']['expected_margin']:+.1f}",
                    f"Prob {analysis['spread_analysis']['prob_cover']:.1%}"
                )
            with col_a2:
                st.metric(
                    "Total Esperado",
                    analysis['totals_analysis']['expected_total'],
                    f"Over {analysis['totals_analysis']['prob_over']:.1%}"
                )
            with col_a3:
                st.metric(
                    "Moneyline",
                    f"{analysis['moneyline_analysis']['home_win_prob']:.1%} vs {analysis['moneyline_analysis']['away_win_prob']:.1%}"
                )
            
            # Aplicar reglas
            picks = self.rules.aplicar_reglas(analysis, game['home'], game['away'])
            st.markdown('**🎯 Picks según reglas NBA:**')
            return picks
