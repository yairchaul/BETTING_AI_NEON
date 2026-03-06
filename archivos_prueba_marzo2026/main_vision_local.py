# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import numpy as np
import math
import json
import time
from datetime import datetime
from modules.elo_system import ELOSystem
from modules.hybrid_data_provider import HybridDataProvider
from modules.smart_betting_ai import SmartBettingAI
from modules.advanced_market_reasoning import AdvancedMarketReasoning
from modules.parlay_generator import build_parlay
from modules.diversification_engine import diversify_picks
from modules.parlay_reasoning_engine import ParlayReasoningEngine

# =============================================================================
# VERSIÓN SIMPLIFICADA DE VISION READER (SIN GOOGLE VISION)
# =============================================================================
class SimpleImageParser:
    """Versión simplificada que usa entrada manual de partidos"""
    
    def process_image(self, img_bytes):
        """Procesa la imagen pero retorna partidos de ejemplo para pruebas"""
        # Aquí puedes poner la lógica de OCR local o usar entrada manual
        return [
            {
                'home': 'Heracles Almelo',
                'away': 'Utrecht',
                'all_odds': ['+215', '+245', '+120']
            },
            {
                'home': 'Groningen',
                'away': 'Ajax Amsterdam',
                'all_odds': ['+166', '+270', '+142']
            },
            {
                'home': 'PSV Eindhoven',
                'away': 'AZ Alkmaar',
                'all_odds': ['-334', '+500', '+710']
            },
            {
                'home': 'Excelsior',
                'away': 'Heerenveen',
                'all_odds': ['+182', '+265', '+130']
            },
            {
                'home': 'Sparta Rotterdam',
                'away': 'Zwolle',
                'all_odds': ['-150', '+310', '+355']
            },
            {
                'home': 'Celta de Vigo',
                'away': 'Real Madrid',
                'all_odds': ['+220', '+230', '+126']
            },
            {
                'home': 'Paris Saint Germain',
                'away': 'AS Monaco',
                'all_odds': ['-286', '+450', '+620']
            },
            {
                'home': 'Napoli',
                'away': 'Torino',
                'all_odds': ['-179', '+290', '+520']
            },
            {
                'home': 'Bayern Munich',
                'away': 'Borussia Mönchengladbach',
                'all_odds': ['-455', '+625', '+880']
            }
        ]

st.set_page_config(page_title="Analizador Profesional de Apuestas", layout="wide")

# =============================================================================
# CLASE PARA REGISTRO DE PARLAYS
# =============================================================================
class ParlayTracker:
    def __init__(self, filepath='data/parlays.json'):
        self.filepath = filepath
        self.parlays = self._load_parlays()
    
    def _load_parlays(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_parlays(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.parlays, f, indent=2, ensure_ascii=False)
    
    def add_parlay(self, picks, prob_total, odds_total, ev_total, stake):
        parlay = {
            'id': len(self.parlays) + 1,
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'picks': picks,
            'prob_total': prob_total,
            'odds_total': odds_total,
            'ev_total': ev_total,
            'stake': stake,
            'estado': 'pendiente',
            'resultado_neto': 0,
            'fecha_verificacion': None
        }
        self.parlays.append(parlay)
        self._save_parlays()
        return parlay
    
    def check_results(self):
        updated = False
        for parlay in self.parlays:
            if parlay['estado'] == 'pendiente':
                import random
                ganado = random.random() < 0.5
                
                if ganado:
                    parlay['estado'] = 'ganado'
                    parlay['resultado_neto'] = parlay['stake'] * (parlay['odds_total'] - 1)
                else:
                    parlay['estado'] = 'perdido'
                    parlay['resultado_neto'] = -parlay['stake']
                
                parlay['fecha_verificacion'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                updated = True
        
        if updated:
            self._save_parlays()
    
    def get_stats(self):
        total = len(self.parlays)
        ganados = sum(1 for p in self.parlays if p['estado'] == 'ganado')
        perdidos = sum(1 for p in self.parlays if p['estado'] == 'perdido')
        pendientes = sum(1 for p in self.parlays if p['estado'] == 'pendiente')
        profit_total = sum(p['resultado_neto'] for p in self.parlays)
        
        return {
            'total': total,
            'ganados': ganados,
            'perdidos': perdidos,
            'pendientes': pendientes,
            'profit_total': profit_total,
            'win_rate': (ganados / (ganados + perdidos)) * 100 if (ganados + perdidos) > 0 else 0
        }

# =============================================================================
# FUNCIONES DE CÁLCULO DE MERCADOS ADICIONALES
# =============================================================================
def calculate_additional_markets(home_stats, away_stats):
    avg_total_goals = home_stats['avg_goals_scored'] + away_stats['avg_goals_scored']
    
    def poisson_prob(k, lam):
        return (math.exp(-lam) * lam**k) / math.factorial(k)
    
    over_1_5 = 1 - poisson_prob(0, avg_total_goals) - poisson_prob(1, avg_total_goals)
    over_2_5 = 1 - sum(poisson_prob(i, avg_total_goals) for i in range(3))
    over_3_5 = 1 - sum(poisson_prob(i, avg_total_goals) for i in range(4))
    
    prob_home_score = 1 - poisson_prob(0, home_stats['avg_goals_scored'])
    prob_away_score = 1 - poisson_prob(0, away_stats['avg_goals_scored'])
    btts_prob = prob_home_score * prob_away_score
    
    lambda_1t = avg_total_goals * 0.35
    over_1_5_1t = 1 - poisson_prob(0, lambda_1t) - poisson_prob(1, lambda_1t)
    over_1_5_1t = min(0.60, over_1_5_1t)
    
    return {
        'over_1_5': over_1_5,
        'over_2_5': over_2_5,
        'over_3_5': over_3_5,
        'btts_yes': btts_prob,
        'btts_no': 1 - btts_prob,
        'over_1_5_1t': over_1_5_1t
    }

# =============================================================================
# FUNCIONES DE FACTORES DE RIESGO
# =============================================================================
def calculate_risk_factors(team_name):
    risk_database = {
        'Tottenham': {
            'red_cards_last_10': 3,
            'key_injuries': ['Van de Ven', 'Romero'],
            'recent_form': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            'consecutive_games': 5,
            'high_pressure': True
        },
        'Crystal Palace': {
            'red_cards_last_10': 1,
            'key_injuries': [],
            'recent_form': [1, 0, 1, 0, 1, 0, 0, 1, 0, 1],
            'consecutive_games': 3,
            'high_pressure': False
        },
        'Arsenal': {
            'red_cards_last_10': 1,
            'key_injuries': ['Jesus'],
            'recent_form': [1, 1, 1, 1, 1, 0, 1, 1, 1, 1],
            'consecutive_games': 4,
            'high_pressure': True
        },
        'Chelsea': {
            'red_cards_last_10': 2,
            'key_injuries': ['James', 'Chilwell'],
            'recent_form': [1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            'consecutive_games': 4,
            'high_pressure': True
        }
    }
    
    default = {
        'red_cards_last_10': 1,
        'key_injuries': [],
        'recent_form': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        'consecutive_games': 2,
        'high_pressure': False
    }
    
    data = risk_database.get(team_name, default)
    risk_score = 1.0
    
    if data['red_cards_last_10'] > 2:
        risk_score *= 0.85
        st.warning(f"⚠️ {team_name}: {data['red_cards_last_10']} expulsiones en últimos 10 partidos")
    elif data['red_cards_last_10'] > 1:
        risk_score *= 0.92
    
    if len(data['key_injuries']) > 1:
        risk_score *= 0.80
        st.warning(f"🩹 {team_name}: Lesiones de {', '.join(data['key_injuries'])}")
    elif len(data['key_injuries']) > 0:
        risk_score *= 0.90
        st.warning(f"🩹 {team_name}: Lesión de {data['key_injuries'][0]}")
    
    last_5 = data['recent_form'][-5:]
    wins = sum(last_5)
    if wins <= 1:
        risk_score *= 0.75
        st.warning(f"📉 {team_name}: Solo {wins} victorias en últimos 5 partidos")
    elif wins <= 2:
        risk_score *= 0.90
    
    if data['consecutive_games'] > 4:
        risk_score *= 0.88
        st.warning(f"⚡ {team_name}: {data['consecutive_games']} partidos en 15 días")
    
    if data.get('high_pressure', False):
        risk_score *= 0.95
        st.info(f"🎯 {team_name}: Partido de alta presión")
    
    return risk_score

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================
def american_to_decimal(american):
    if not american or american == 'N/A':
        return 2.0
    try:
        american = str(american).replace('+', '')
        american = int(american)
        if american > 0:
            return round(1 + (american / 100), 2)
        else:
            return round(1 + (100 / abs(american)), 2)
    except:
        return 2.0

def find_best_over(additional_markets):
    overs = [
        ('Over 1.5', additional_markets['over_1_5']),
        ('Over 2.5', additional_markets['over_2_5']),
        ('Over 3.5', additional_markets['over_3_5'])
    ]
    valid_overs = [(name, prob) for name, prob in overs if prob > 0.55]
    
    if valid_overs:
        return min(valid_overs, key=lambda x: abs(x[1] - 0.55))
    else:
        return max(overs, key=lambda x: x[1])

def find_best_simple_market(additional_markets, probs_1x2, home, away):
    markets = [
        ('Over 1.5', additional_markets['over_1_5']),
        ('Over 2.5', additional_markets['over_2_5']),
        ('Over 3.5', additional_markets['over_3_5']),
        ('BTTS Sí', additional_markets['btts_yes']),
        (f"Gana {home}", probs_1x2['home']),
        ('Empate', probs_1x2['draw']),
        (f"Gana {away}", probs_1x2['away'])
    ]
    return max(markets, key=lambda x: x[1])

def select_parlay_picks(additional_markets, probs_1x2, home, away):
    home_win = probs_1x2['home']
    away_win = probs_1x2['away']
    over_1_5_1t = additional_markets['over_1_5_1t']
    btts = additional_markets['btts_yes']
    
    picks = []
    
    if over_1_5_1t > 0.50:
        picks.append({
            'market': 'Over 1.5 1T',
            'prob': over_1_5_1t,
            'type': 'over_1t',
            'level': 1
        })
        return picks
    
    if btts > 0.50:
        picks.append({
            'market': 'BTTS Sí',
            'prob': btts,
            'type': 'btts',
            'level': 2
        })
        return picks
    
    best_over_name, best_over_prob = find_best_over(additional_markets)
    
    if home_win > 0.50 and away_win < 0.40:
        home_risk = calculate_risk_factors(home)
        away_risk = calculate_risk_factors(away)
        
        adjusted_home_win = home_win * home_risk
        upset_factor = 1.0 + (0.2 * (1 - away_risk))
        adjusted_home_win = min(adjusted_home_win * upset_factor, home_win * 1.1)
        
        if adjusted_home_win > 0.45:
            picks.append({
                'market': f"Gana {home}",
                'prob': adjusted_home_win,
                'type': 'home_win_risk',
                'level': 4,
                'note': f"Riesgo: {1-home_risk:.0%}"
            })
            picks.append({
                'market': best_over_name,
                'prob': best_over_prob,
                'type': 'over',
                'level': 4
            })
        else:
            picks.append({
                'market': best_over_name,
                'prob': best_over_prob,
                'type': 'over',
                'level': 3
            })
    
    elif away_win > 0.50 and home_win < 0.40:
        home_risk = calculate_risk_factors(home)
        away_risk = calculate_risk_factors(away)
        
        adjusted_away_win = away_win * away_risk
        upset_factor = 1.0 + (0.2 * (1 - home_risk))
        adjusted_away_win = min(adjusted_away_win * upset_factor, away_win * 1.1)
        
        if adjusted_away_win > 0.45:
            picks.append({
                'market': f"Gana {away}",
                'prob': adjusted_away_win,
                'type': 'away_win_risk',
                'level': 5,
                'note': f"Riesgo: {1-away_risk:.0%}"
            })
            picks.append({
                'market': best_over_name,
                'prob': best_over_prob,
                'type': 'over',
                'level': 5
            })
        else:
            picks.append({
                'market': best_over_name,
                'prob': best_over_prob,
                'type': 'over',
                'level': 3
            })
    
    else:
        picks.append({
            'market': best_over_name,
            'prob': best_over_prob,
            'type': 'over',
            'level': 3
        })
    
    return picks

# =============================================================================
# INICIALIZACIÓN DE COMPONENTES
# =============================================================================
@st.cache_resource
def init_components():
    return {
        'vision': SimpleImageParser(),
        'elo': ELOSystem(),
        'data_provider': HybridDataProvider(),
        'betting_ai': SmartBettingAI(league_avg_goals=2.6),
        'market_reasoning': AdvancedMarketReasoning(),
        'tracker': ParlayTracker(),
        'reasoning_engine': ParlayReasoningEngine(umbral_principal=0.50)
    }

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================
def main():
    st.title("🎯 Analizador Profesional de Apuestas")
    st.markdown("**Sistema con REGLA 6 - Umbral 50%**")

    components = init_components()

    with st.sidebar:
        st.header("⚙️ Configuración")
        bankroll = st.number_input("Bankroll ($)", 100, 10000, 1000)
        min_ev = st.slider("EV mínimo", 0.0, 0.2, 0.05, 0.01)
        
        st.divider()
        st.subheader("📊 Estadísticas")
        stats = components['tracker'].get_stats()
        st.metric("Parlays totales", stats['total'])
        st.metric("Ganados", stats['ganados'])
        st.metric("Perdidos", stats['perdidos'])
        st.metric("Win Rate", f"{stats['win_rate']:.1f}%")
        st.metric("Profit total", f"${stats['profit_total']:.2f}")
        
        if st.button("🔄 Verificar resultados"):
            components['tracker'].check_results()
            st.rerun()
        
        st.divider()
        st.subheader("📸 Capturas manuales")
        st.info("Usando datos de ejemplo para pruebas")

    uploaded_file = st.file_uploader("Sube tu captura de Caliente.mx", type=['png', 'jpg', 'jpeg'])

    if uploaded_file:
        img_bytes = uploaded_file.getvalue()
        st.image(img_bytes, use_container_width=True)

        with st.spinner("🔍 Analizando imagen..."):
            matches = components['vision'].process_image(img_bytes)

        if matches:
            st.success(f"✅ Partidos detectados: {len(matches)}")

            df_data = []
            for match in matches:
                odds = match.get('all_odds', ['N/A', 'N/A', 'N/A'])
                df_data.append({
                    'Local': match.get('home', 'N/A'),
                    'L': odds[0],
                    'Empate': 'Empate',
                    'E': odds[1],
                    'Visitante': match.get('away', 'N/A'),
                    'V': odds[2]
                })
            st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)

            st.subheader("📊 Análisis por partido")
            all_parlay_picks = []

            for i, match in enumerate(matches):
                home = match.get('home', '')
                away = match.get('away', '')
                odds = match.get('all_odds', ['N/A', 'N/A', 'N/A'])

                dec_local = american_to_decimal(odds[0])
                dec_empate = american_to_decimal(odds[1])
                dec_visit = american_to_decimal(odds[2])

                with st.expander(f"**{home} vs {away}**", expanded=(i == 0)):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Local", odds[0], f"{dec_local:.2f}")
                    with col2:
                        st.metric("Empate", odds[1], f"{dec_empate:.2f}")
                    with col3:
                        st.metric("Visitante", odds[2], f"{dec_visit:.2f}")

                    home_stats = components['data_provider'].get_team_stats(home)
                    away_stats = components['data_provider'].get_team_stats(away)
                    
                    st.caption(f"📈 {home}: {home_stats['avg_goals_scored']:.2f} GF | {away}: {away_stats['avg_goals_scored']:.2f} GF")

                    additional_markets = calculate_additional_markets(home_stats, away_stats)
                    probs_1x2 = components['elo'].get_win_probability(home, away, home_stats, away_stats)
                    
                    st.markdown("**📈 Mercados Adicionales:**")
                    
                    col_m1, col_m2, col_m3 = st.columns(3)
                    with col_m1:
                        st.metric("Over 1.5", f"{additional_markets['over_1_5']:.1%}")
                    with col_m2:
                        st.metric("BTTS Sí", f"{additional_markets['btts_yes']:.1%}")
                    with col_m3:
                        st.metric("Gana Local", f"{probs_1x2['home']:.1%}")
                    
                    col_n1, col_n2, col_n3 = st.columns(3)
                    with col_n1:
                        st.metric("Over 2.5", f"{additional_markets['over_2_5']:.1%}")
                    with col_n2:
                        st.metric("BTTS No", f"{additional_markets['btts_no']:.1%}")
                    with col_n3:
                        st.metric("Empate", f"{probs_1x2['draw']:.1%}")
                    
                    col_o1, col_o2, col_o3 = st.columns(3)
                    with col_o1:
                        st.metric("Over 3.5", f"{additional_markets['over_3_5']:.1%}")
                    with col_o2:
                        st.metric("Over 1.5 1T", f"{additional_markets['over_1_5_1t']:.1%}")
                    with col_o3:
                        st.metric("Gana Visitante", f"{probs_1x2['away']:.1%}")

                    ev_local = (probs_1x2['home'] * dec_local) - 1
                    ev_draw = (probs_1x2['draw'] * dec_empate) - 1
                    ev_away = (probs_1x2['away'] * dec_visit) - 1
                    
                    if ev_local > min_ev:
                        st.success(f"🔥 Local: EV +{ev_local:.1%}")
                    if ev_draw > min_ev:
                        st.success(f"🔥 Empate: EV +{ev_draw:.1%}")
                    if ev_away > min_ev:
                        st.success(f"🔥 Visitante: EV +{ev_away:.1%}")

                    parlay_picks = select_parlay_picks(additional_markets, probs_1x2, home, away)
                    
                    st.markdown("**🎯 Picks para parlay:**")
                    for pick in parlay_picks:
                        note = f" - {pick['note']}" if 'note' in pick else ""
                        st.markdown(f"• Nivel {pick['level']}: **{pick['market']}** ({pick['prob']:.1%}){note}")
                        
                        fair_odds = 1 / pick['prob'] if pick['prob'] > 0 else 2.0
                        market_odds = fair_odds * 0.95
                        ev_value = (pick['prob'] * market_odds) - 1
                        
                        all_parlay_picks.append({
                            'match': f"{home} vs {away}",
                            'market': pick['market'],
                            'prob': pick['prob'],
                            'odds': market_odds,
                            'ev': ev_value,
                            'level': pick['level'],
                            'home': home,
                            'away': away,
                            'note': pick.get('note', '')
                        })

            # =========================================================================
            # PARLAY RECOMENDADO CON REGLA 6
            # =========================================================================
            if len(all_parlay_picks) >= 2:
                st.divider()
                st.subheader("🎯 PARLAY RECOMENDADO")
                
                # Agrupar picks por partido - CORREGIDO para usar 'market' en lugar de 'mercado'
                partidos_con_picks = {}
                for pick in all_parlay_picks:
                    match_key = pick['match']
                    if match_key not in partidos_con_picks:
                        partidos_con_picks[match_key] = []
                    
                    # Convertir al formato esperado por el motor de razonamiento
                    partidos_con_picks[match_key].append({
                        'partido': pick['match'],
                        'mercado': pick['market'],  # Convertimos 'market' a 'mercado'
                        'prob': pick['prob'],
                        'odds': pick['odds']
                    })
                
                # Usar motor de razonamiento
                picks_finales = components['reasoning_engine'].construir_parlay_por_partido(partidos_con_picks)
                
                st.markdown("### 🎯 SELECCIONES FINALES")
                total_prob = 1.0
                total_odds = 1.0
                
                for pick in picks_finales:
                    if pick.get('tipo') == 'combinado':
                        st.markdown(f"📦 {pick['partido']}: **COMBINADO**")
                        for p in pick['picks']:
                            st.markdown(f"   - {p['mercado']} ({p['prob']:.1%})")
                            total_prob *= p['prob']
                            total_odds *= p.get('odds', 1.95)
                    else:
                        st.markdown(f"• {pick['match']}: **{pick.get('mercado', pick.get('market', 'N/A'))}** ({pick['prob']:.1%})")
                        total_prob *= pick['prob']
                        total_odds *= pick.get('odds', 1.95)
                
                ev_total = (total_prob * total_odds) - 1
                
                st.markdown("---")
                col_p1, col_p2, col_p3 = st.columns(3)
                with col_p1:
                    st.metric("Probabilidad total", f"{total_prob:.1%}")
                with col_p2:
                    st.metric("Cuota total", f"{total_odds:.2f}")
                with col_p3:
                    delta_color = "normal" if ev_total > 0 else "inverse"
                    st.metric("EV total", f"{ev_total:.1%}", delta_color=delta_color)
                
                if ev_total > 0:
                    cuota = total_odds
                    if cuota > 1:
                        kelly = ev_total / (cuota - 1) * 0.25
                        stake = min(kelly * bankroll, bankroll * 0.1)
                        st.success(f"💰 Stake sugerido: ${stake:.2f}")
                        
                        if st.button("📝 Registrar este parlay"):
                            picks_guardar = []
                            for pick in picks_finales:
                                picks_guardar.append({
                                    'match': pick.get('partido', pick.get('match', '')),
                                    'market': pick.get('mercado', pick.get('market', 'COMBINADO')),
                                    'prob': pick.get('prob', 0)
                                })
                            
                            components['tracker'].add_parlay(
                                picks_guardar,
                                total_prob,
                                total_odds,
                                ev_total,
                                stake
                            )
                            st.success("✅ Parlay registrado!")
                            time.sleep(1)
                            st.rerun()
        else:
            st.error("❌ No se detectaron partidos")

if __name__ == "__main__":
    main()
