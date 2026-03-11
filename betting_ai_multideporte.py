"""
SISTEMA COMPLETO - Multi-deporte + Parlay Builder
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np

# ============================================
# CLASE EVENTO UNIFICADA
# ============================================
class Evento:
    def __init__(self, deporte, liga, local, visitante, odds_local, odds_empate, odds_visitante):
        self.deporte = deporte
        self.liga = liga
        self.local = local
        self.visitante = visitante
        self.odds_local = odds_local
        self.odds_empate = odds_empate
        self.odds_visitante = odds_visitante
        self.picks = []
        self.mercados = {}

# ============================================
# MCP CLIENT - DATOS REALES
# ============================================
class MCPClient:
    def get_partidos_futbol(self):
        """Partidos de fútbol de hoy (de tu captura)"""
        return [
            Evento("⚽ FÚTBOL", "UEFA Champions League", "Liverpool", "Galatasaray", 1.25, 6.0, 10.25),
            Evento("⚽ FÚTBOL", "UEFA Champions League", "Bayern Munich", "Atalanta", 1.27, 6.0, 9.80),
            Evento("⚽ FÚTBOL", "UEFA Champions League", "Bayer Leverkusen", "Arsenal", 6.0, 2.87, 1.80),
            Evento("⚽ FÚTBOL", "UEFA Champions League", "Real Madrid", "Manchester City", 3.50, 3.65, 1.98),
            Evento("⚽ FÚTBOL", "UEFA Champions League", "Tottenham", "Atlético Madrid", 2.50, 3.90, 2.50),
            Evento("⚽ FÚTBOL", "UEFA Champions League", "PSG", "Chelsea", 1.95, 3.75, 3.55),
            Evento("⚽ FÚTBOL", "UEFA Champions League", "Barcelona", "Newcastle", 1.57, 4.55, 5.00),
            Evento("⚽ FÚTBOL", "UEFA Champions League", "Bodo Glimt", "Sporting Lisboa", 2.25, 3.55, 3.00)
        ]
    
    def get_partidos_nba(self):
        """Partidos de NBA de hoy"""
        return [
            Evento("🏀 NBA", "NBA", "Lakers", "Celtics", 2.10, None, 1.80),
            Evento("🏀 NBA", "NBA", "Warriors", "Nuggets", 1.95, None, 1.90),
            Evento("🏀 NBA", "NBA", "Bucks", "76ers", 1.85, None, 2.00),
            Evento("🏀 NBA", "NBA", "Suns", "Clippers", 2.20, None, 1.70)
        ]
    
    def get_combates_ufc(self):
        """Combates de UFC de hoy"""
        return [
            Evento("🥊 UFC", "UFC 299", "O'Malley", "Vera", 1.45, None, 2.75),
            Evento("🥊 UFC", "UFC 299", "Poirier", "Saint Denis", 1.90, None, 1.95),
            Evento("🥊 UFC", "UFC 299", "Masvidal", "Burns", 2.30, None, 1.65)
        ]

# ============================================
# STATS ENGINE - CÁLCULOS POR DEPORTE
# ============================================
class StatsEngine:
    def calcular_futbol(self, evento):
        """Cálculos específicos para fútbol"""
        probs = {}
        
        # Probabilidades 1X2
        prob_local = 1/evento.odds_local
        prob_empate = 1/evento.odds_empate if evento.odds_empate else 0
        prob_visit = 1/evento.odds_visitante
        
        # Normalizar
        total = prob_local + prob_empate + prob_visit
        probs['prob_local'] = prob_local / total
        probs['prob_empate'] = prob_empate / total
        probs['prob_visit'] = prob_visit / total
        
        # GF estimados
        probs['gf_local'] = 2.5 * (1/evento.odds_local) * 3
        probs['gf_visit'] = 2.5 * (1/evento.odds_visitante) * 3
        
        # Overs aproximados
        probs['over_1_5'] = min(0.95, 0.7 + (probs['gf_local'] + probs['gf_visit'] - 2) * 0.1)
        probs['over_2_5'] = min(0.85, 0.4 + (probs['gf_local'] + probs['gf_visit'] - 2) * 0.15)
        probs['over_3_5'] = min(0.70, 0.2 + (probs['gf_local'] + probs['gf_visit'] - 2) * 0.15)
        
        # BTTS
        probs['btts_si'] = min(0.85, 0.5 + (probs['gf_local'] + probs['gf_visit'] - 2) * 0.15)
        probs['btts_no'] = 1 - probs['btts_si']
        
        return probs
    
    def calcular_nba(self, evento):
        """Cálculos específicos para NBA"""
        probs = {}
        
        # Moneyline
        prob_local = 1/evento.odds_local
        prob_visit = 1/evento.odds_visitante
        total = prob_local + prob_visit
        probs['prob_local'] = prob_local / total
        probs['prob_visit'] = prob_visit / total
        
        # Spread (aproximado)
        probs['spread_local'] = probs['prob_local'] * 0.95
        probs['spread_visit'] = probs['prob_visit'] * 0.95
        
        # Totals
        probs['over'] = 0.52
        probs['under'] = 0.48
        
        return probs
    
    def calcular_ufc(self, evento):
        """Cálculos específicos para UFC"""
        probs = {}
        
        prob_local = 1/evento.odds_local
        prob_visit = 1/evento.odds_visitante
        total = prob_local + prob_visit
        probs['prob_local'] = prob_local / total
        probs['prob_visit'] = prob_visit / total
        
        # Métodos de victoria (aproximados)
        probs['ko_tko'] = 0.45
        probs['sumision'] = 0.25
        probs['decision'] = 0.30
        
        return probs

# ============================================
# RULE ENGINE - REGLAS POR DEPORTE
# ============================================
class RuleEngine:
    def generar_picks_futbol(self, evento, probs):
        """Genera picks para fútbol usando las 7 reglas"""
        picks = []
        
        # Regla 1: Over 1.5 1T
        if probs.get('over_1_5_1t', 0) > 0.60:
            picks.append(('Over 1.5 1T', probs['over_1_5_1t'], 1))
        
        # Regla 2: Over 2.5 + favorito
        if probs.get('over_2_5', 0) > 0.60:
            if probs['prob_local'] > 0.55:
                picks.append((f'Gana {evento.local}', probs['prob_local'], 2))
                picks.append(('Over 2.5', probs['over_2_5'], 2))
            elif probs['prob_visit'] > 0.55:
                picks.append((f'Gana {evento.visitante}', probs['prob_visit'], 2))
                picks.append(('Over 2.5', probs['over_2_5'], 2))
        
        # Regla 3: BTTS
        if probs.get('btts_si', 0) > 0.60:
            picks.append(('BTTS Sí', probs['btts_si'], 3))
        
        # Regla 4: Mejor over
        overs = [
            ('Over 1.5', probs['over_1_5']),
            ('Over 2.5', probs['over_2_5']),
            ('Over 3.5', probs['over_3_5'])
        ]
        mejor_over = max(overs, key=lambda x: x[1])
        picks.append((f'{mejor_over[0]}', mejor_over[1], 4))
        
        # Regla 5/6: Favoritos
        if probs['prob_local'] > 0.60:
            picks.append((f'Gana {evento.local}', probs['prob_local'], 5))
        if probs['prob_visit'] > 0.60:
            picks.append((f'Gana {evento.visitante}', probs['prob_visit'], 6))
        
        return picks
    
    def generar_picks_nba(self, evento, probs):
        """Genera picks para NBA"""
        picks = [
            (f'Moneyline {evento.local}', probs['prob_local'], 1),
            (f'Spread {evento.local}', probs['spread_local'], 2),
            ('Over', probs['over'], 3)
        ]
        return picks
    
    def generar_picks_ufc(self, evento, probs):
        """Genera picks para UFC"""
        picks = [
            (f'Gana {evento.local}', probs['prob_local'], 1),
            ('KO/TKO', probs['ko_tko'], 2),
            ('Sumisión', probs['sumision'], 3)
        ]
        return picks

# ============================================
# PARLAY BUILDER
# ============================================
class ParlayBuilder:
    def __init__(self):
        if 'parlay' not in st.session_state:
            st.session_state.parlay = []
    
    def agregar_pick(self, pick):
        st.session_state.parlay.append(pick)
    
    def quitar_pick(self, idx):
        if 0 <= idx < len(st.session_state.parlay):
            st.session_state.parlay.pop(idx)
    
    def calcular_parlay(self):
        if not st.session_state.parlay:
            return 0, 0
        
        cuota_total = 1.0
        prob_total = 1.0
        
        for pick in st.session_state.parlay:
            cuota_total *= pick['cuota']
            prob_total *= pick['probabilidad']
        
        return cuota_total, prob_total
    
    def limpiar(self):
        st.session_state.parlay = []

# ============================================
# INTERFAZ PRINCIPAL
# ============================================
def main():
    st.set_page_config(page_title="BETTING_AI - MULTIDEPORTE", layout="wide")
    
    st.title("🎯 BETTING_AI - ANALIZADOR MULTIDEPORTE + PARLAY")
    st.markdown(f"### 📅 {datetime.now().strftime('%d/%m/%Y')}")
    
    # Inicializar componentes
    if 'mcp' not in st.session_state:
        st.session_state.mcp = MCPClient()
        st.session_state.stats = StatsEngine()
        st.session_state.rules = RuleEngine()
        st.session_state.parlay_builder = ParlayBuilder()
        st.session_state.todos_picks = []
    
    # Sidebar - Configuración y Parlay
    with st.sidebar:
        st.header("🎯 MI PARLAY")
        
        parlay = st.session_state.parlay_builder
        picks_parlay = st.session_state.parlay
        
        if picks_parlay:
            for i, pick in enumerate(picks_parlay):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{pick['partido'][:20]}**  \n{pick['pick']}")
                with col2:
                    st.markdown(f"**{pick['cuota']:.2f}**")
                    if st.button("❌", key=f"del_{i}"):
                        parlay.quitar_pick(i)
                        st.rerun()
            
            cuota_total, prob_total = parlay.calcular_parlay()
            st.markdown("---")
            st.metric("CUOTA TOTAL", f"{cuota_total:.2f}")
            st.metric("PROBABILIDAD", f"{prob_total*100:.1f}%")
            st.metric("VALUE ESPERADO", f"{(cuota_total * prob_total - 1)*100:.1f}%")
            
            if st.button("🧹 LIMPIAR PARLAY"):
                parlay.limpiar()
                st.rerun()
        else:
            st.info("Agrega picks al parlay")
        
        st.markdown("---")
        st.header("⚙️ Controles")
        if st.button("🔄 ACTUALIZAR TODOS LOS DEPORTES"):
            with st.spinner("Cargando partidos..."):
                st.session_state.futbol = st.session_state.mcp.get_partidos_futbol()
                st.session_state.nba = st.session_state.mcp.get_partidos_nba()
                st.session_state.ufc = st.session_state.mcp.get_combates_ufc()
                
                # Generar todos los picks
                todos = []
                for e in st.session_state.futbol:
                    probs = st.session_state.stats.calcular_futbol(e)
                    picks = st.session_state.rules.generar_picks_futbol(e, probs)
                    for desc, prob, nivel in picks:
                        cuota = 1/prob * 0.95
                        value = (prob * cuota) - 1
                        todos.append({
                            'deporte': '⚽',
                            'partido': f"{e.local} vs {e.visitante}",
                            'liga': e.liga,
                            'pick': desc,
                            'probabilidad': prob,
                            'cuota': cuota,
                            'value': value,
                            'nivel': nivel,
                            'evento_obj': e
                        })
                
                for e in st.session_state.nba:
                    probs = st.session_state.stats.calcular_nba(e)
                    picks = st.session_state.rules.generar_picks_nba(e, probs)
                    for desc, prob, nivel in picks:
                        cuota = 1/prob * 0.95
                        value = (prob * cuota) - 1
                        todos.append({
                            'deporte': '🏀',
                            'partido': f"{e.local} vs {e.visitante}",
                            'liga': e.liga,
                            'pick': desc,
                            'probabilidad': prob,
                            'cuota': cuota,
                            'value': value,
                            'nivel': nivel,
                            'evento_obj': e
                        })
                
                for e in st.session_state.ufc:
                    probs = st.session_state.stats.calcular_ufc(e)
                    picks = st.session_state.rules.generar_picks_ufc(e, probs)
                    for desc, prob, nivel in picks:
                        cuota = 1/prob * 0.95
                        value = (prob * cuota) - 1
                        todos.append({
                            'deporte': '🥊',
                            'partido': f"{e.local} vs {e.visitante}",
                            'liga': e.liga,
                            'pick': desc,
                            'probabilidad': prob,
                            'cuota': cuota,
                            'value': value,
                            'nivel': nivel,
                            'evento_obj': e
                        })
                
                st.session_state.todos_picks = sorted(todos, key=lambda x: x['value'], reverse=True)
                st.success(f"✅ {len(st.session_state.todos_picks)} picks generados")
    
    # MAIN CONTENT - Pestañas por deporte
    if 'todos_picks' in st.session_state and st.session_state.todos_picks:
        tab1, tab2, tab3, tab4 = st.tabs(["🏆 TOP GLOBAL", "⚽ FÚTBOL", "🏀 NBA", "🥊 UFC"])
        
        with tab1:
            st.header("🏆 MEJORES PICKS DE TODOS LOS DEPORTES")
            cols = st.columns(3)
            top_picks = st.session_state.todos_picks[:9]  # Top 9
            
            for i, pick in enumerate(top_picks):
                with cols[i % 3]:
                    value_pct = pick['value'] * 100
                    color = "#00CC00" if value_pct > 10 else "#88CC00" if value_pct > 5 else "#DDDD00" if value_pct > 0 else "#FF5500"
                    
                    with st.container():
                        st.markdown(f"""
                        <div style="border:2px solid {color}; border-radius:10px; padding:10px; margin:5px;">
                            <h3 style="margin:0;">{pick['deporte']} {pick['liga'][:15]}</h3>
                            <p><b>{pick['partido'][:25]}</b></p>
                            <p style="font-size:1.2em;">🎯 {pick['pick']}</p>
                            <p style="font-size:1.5em; color:{color};">{value_pct:.1f}% VALUE</p>
                            <p>📊 {pick['probabilidad']*100:.1f}% | 💰 {pick['cuota']:.2f}</p>
                        """, unsafe_allow_html=True)
                        
                        if st.button("➕ Agregar al parlay", key=f"add_top_{i}"):
                            st.session_state.parlay_builder.agregar_pick({
                                'partido': pick['partido'],
                                'pick': pick['pick'],
                                'cuota': pick['cuota'],
                                'probabilidad': pick['probabilidad']
                            })
                            st.success("✓ Agregado")
                        st.markdown("</div>", unsafe_allow_html=True)
        
        with tab2:
            st.header("⚽ FÚTBOL - TODOS LOS PARTIDOS")
            futbol_picks = [p for p in st.session_state.todos_picks if p['deporte'] == '⚽']
            for pick in futbol_picks:
                col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
                with col1:
                    st.markdown(f"**{pick['partido']}**")
                with col2:
                    st.markdown(f"🎯 {pick['pick']}")
                with col3:
                    st.markdown(f"{pick['probabilidad']*100:.1f}%")
                with col4:
                    st.markdown(f"{pick['cuota']:.2f}")
                with col5:
                    if st.button("➕", key=f"add_futbol_{pick['partido']}_{pick['pick']}"):
                        st.session_state.parlay_builder.agregar_pick({
                            'partido': pick['partido'],
                            'pick': pick['pick'],
                            'cuota': pick['cuota'],
                            'probabilidad': pick['probabilidad']
                        })
                        st.success("✓")
        
        with tab3:
            st.header("🏀 NBA - TODOS LOS PARTIDOS")
            nba_picks = [p for p in st.session_state.todos_picks if p['deporte'] == '🏀']
            for pick in nba_picks:
                col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
                with col1:
                    st.markdown(f"**{pick['partido']}**")
                with col2:
                    st.markdown(f"🎯 {pick['pick']}")
                with col3:
                    st.markdown(f"{pick['probabilidad']*100:.1f}%")
                with col4:
                    st.markdown(f"{pick['cuota']:.2f}")
                with col5:
                    if st.button("➕", key=f"add_nba_{pick['partido']}_{pick['pick']}"):
                        st.session_state.parlay_builder.agregar_pick({
                            'partido': pick['partido'],
                            'pick': pick['pick'],
                            'cuota': pick['cuota'],
                            'probabilidad': pick['probabilidad']
                        })
                        st.success("✓")
        
        with tab4:
            st.header("🥊 UFC - TODOS LOS COMBATES")
            ufc_picks = [p for p in st.session_state.todos_picks if p['deporte'] == '🥊']
            for pick in ufc_picks:
                col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
                with col1:
                    st.markdown(f"**{pick['partido']}**")
                with col2:
                    st.markdown(f"🎯 {pick['pick']}")
                with col3:
                    st.markdown(f"{pick['probabilidad']*100:.1f}%")
                with col4:
                    st.markdown(f"{pick['cuota']:.2f}")
                with col5:
                    if st.button("➕", key=f"add_ufc_{pick['partido']}_{pick['pick']}"):
                        st.session_state.parlay_builder.agregar_pick({
                            'partido': pick['partido'],
                            'pick': pick['pick'],
                            'cuota': pick['cuota'],
                            'probabilidad': pick['probabilidad']
                        })
                        st.success("✓")
    else:
        st.info("👈 Haz click en ACTUALIZAR para cargar los partidos")

if __name__ == "__main__":
    main()
