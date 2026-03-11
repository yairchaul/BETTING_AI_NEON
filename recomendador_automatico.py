"""
Recomendador Automático - CON 8 PARTIDOS y CÁLCULOS REALES
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from mcp_client import MCPOddsClient
from stats_engine import StatsEngine
from rule_engine import RuleEngine
from evento import Evento

class RecomendadorAutomatico:
    def __init__(self):
        self.mcp = MCPOddsClient()
        self.stats = StatsEngine()
        self.rules = RuleEngine()
        
    def obtener_partidos_hoy(self):
        """Extrae TODOS los partidos"""
        datos = self.mcp.get_odds("soccer", "mx,us,uk,eu")
        return [self._api_a_evento(d) for d in datos]
    
    def _api_a_evento(self, data):
        bookmaker = data['bookmakers'][0] if data['bookmakers'] else None
        odds_dict = {}
        
        if bookmaker:
            for market in bookmaker['markets']:
                if market['key'] == 'h2h':
                    for outcome in market['outcomes']:
                        odds_dict[outcome['name']] = outcome['price']
        
        return Evento(
            deporte="FUTBOL",
            competencia=data['sport_title'],
            equipo_local=data['home_team'],
            equipo_visitante=data['away_team'],
            odds_local=odds_dict.get(data['home_team'], 0),
            odds_empate=odds_dict.get('Draw', 0),
            odds_visitante=odds_dict.get(data['away_team'], 0)
        )
    
    def analizar_todo(self, partidos):
        """Analiza todos los partidos y genera recomendaciones"""
        todas = []
        
        for evento in partidos:
            # Calcular probabilidades
            probs = self.stats.calcular(evento)
            evento.mercados = probs
            
            # Aplicar 7 reglas
            picks = self.rules.aplicar_reglas(evento, probs)
            evento.value_bets = picks
            
            # Guardar cada pick
            for pick in picks:
                prob = pick.get('probabilidad', 0)
                cuota = pick.get('odds', 0)
                nivel = pick.get('nivel', 7)
                
                # VALUE = (probabilidad * cuota) - 1
                value = (prob * cuota) - 1
                
                todas.append({
                    'partido': f"{evento.equipo_local} vs {evento.equipo_visitante}",
                    'liga': evento.competencia,
                    'pick': pick.get('descripcion', pick.get('mercado')),
                    'probabilidad': prob,
                    'cuota': cuota,
                    'value': value,
                    'nivel': nivel,
                    'score': value * (1 + (7 - nivel)/10),
                    'gf_local': probs.get('gf_local', 0),
                    'gf_visit': probs.get('gf_visitante', 0)
                })
        
        return sorted(todas, key=lambda x: x['score'], reverse=True)

def main():
    st.set_page_config(page_title="BETTING_AI - REAL", layout="wide")
    
    st.title("🎯 BETTING_AI - RECOMENDADOR EN TIEMPO REAL")
    st.markdown(f"### 📅 Partidos de hoy: {datetime.now().strftime('%d/%m/%Y')}")
    
    if 'recomendador' not in st.session_state:
        st.session_state.recomendador = RecomendadorAutomatico()
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("🚀 ACTUALIZAR PARTIDOS", use_container_width=True):
            with st.spinner("Extrayendo partidos..."):
                partidos = st.session_state.recomendador.obtener_partidos_hoy()
                st.session_state.partidos_raw = partidos
                st.session_state.recomendaciones = st.session_state.recomendador.analizar_todo(partidos)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuración")
        st.info("""
        **¿Cómo funciona?**
        1. Click ACTUALIZAR
        2. Extrae TODOS los partidos
        3. Calcula Poisson
        4. Aplica 7 reglas
        5. Muestra TOP recomendaciones
        """)
        
        if 'recomendaciones' in st.session_state:
            recs = st.session_state.recomendaciones
            st.metric("Partidos hoy", len(st.session_state.partidos_raw))
            if recs:
                values = [r['value']*100 for r in recs[:5]]
                st.metric("Mejor value", f"{max(values):.1f}%")
                st.metric("Value promedio", f"{sum(values)/len(values):.1f}%")
    
    # Mostrar TOP 5
    if 'recomendaciones' in st.session_state and st.session_state.recomendaciones:
        top_5 = st.session_state.recomendaciones[:5]
        
        st.header("🏆 TOP 5 RECOMENDACIONES")
        cols = st.columns(5)
        
        for i, rec in enumerate(top_5):
            with cols[i]:
                value_pct = rec['value'] * 100
                if value_pct > 10:
                    color = "#00CC00"
                elif value_pct > 5:
                    color = "#88CC00"
                elif value_pct > 0:
                    color = "#DDDD00"
                else:
                    color = "#FF5500"
                
                st.markdown(f"""
                <div style="border:3px solid {color}; border-radius:15px; padding:15px; margin:5px;">
                    <h2 style="text-align:center;">#{i+1}</h2>
                    <h4 style="text-align:center;">{rec['liga'][:20]}</h4>
                    <h3 style="color:#2E86AB; text-align:center;">{rec['partido'][:20]}...</h3>
                    <p style="font-size:1.3em; text-align:center;"><b>{rec['pick']}</b></p>
                    <p style="font-size:1.8em; color:{color}; text-align:center;"><b>{value_pct:.1f}% VALUE</b></p>
                    <p style="text-align:center;">📊 {rec['probabilidad']*100:.1f}% | 💰 {rec['cuota']:.2f}</p>
                    <p style="text-align:center;">🎯 Nivel {rec['nivel']} | ⚽ GF: {rec['gf_local']:.1f}-{rec['gf_visit']:.1f}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Tabla completa
        with st.expander("📋 Ver TODOS los partidos analizados"):
            df = pd.DataFrame(st.session_state.recomendaciones)
            df['probabilidad'] = df['probabilidad'].apply(lambda x: f"{x*100:.1f}%")
            df['value'] = df['value'].apply(lambda x: f"{x*100:.1f}%")
            st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()
