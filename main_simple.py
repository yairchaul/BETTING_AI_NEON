import streamlit as st
import pandas as pd
import numpy as np
from modules.universal_parser import UniversalParser
from modules.pro_analyzer_simple import ProAnalyzerSimple
from modules.odds_api_integrator import OddsAPIIntegrator
from core.data_acquisition.ufc_real_api import UFCRealAPI

st.set_page_config(page_title="Analizador de Apuestas", layout="wide")

@st.cache_resource
def init_components():
    return {
        'parser': UniversalParser(),
        'analyzer': ProAnalyzerSimple(),
        'odds_api': OddsAPIIntegrator()
    }

components = init_components()

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

def main():
    st.title(" Analizador de Apuestas (Simplificado)")
    st.markdown("**Basado en datos REALES de 2026**")

    with st.sidebar:
        st.header(" Configuración")
        bankroll = st.number_input("Bankroll ($)", 100, 10000, 1000)
        min_ev = st.slider("EV mínimo", 0.0, 0.2, 0.05, 0.01)
        debug = st.checkbox("Modo debug")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("1. Sube tu captura")
        uploaded_file = st.file_uploader("Selecciona imagen", type=['png', 'jpg', 'jpeg'])
        if uploaded_file:
            st.image(uploaded_file, use_container_width=True)

    if uploaded_file:
        with st.spinner(" Procesando..."):
            img_bytes = uploaded_file.getvalue()
            
            from google.cloud import vision
            client = vision.ImageAnnotatorClient()
            image = vision.Image(content=img_bytes)
            response = client.text_detection(image=image)
            
            if response.text_annotations:
                raw_text = response.text_annotations[0].description
                matches = components['parser'].parse(raw_text)
                st.info(f" Partidos detectados: {len(matches)}")
            else:
                st.error("No se detectó texto")
                return

        if matches:
            with col2:
                st.subheader(f"2. Partidos detectados")
                df_view = []
                for m in matches:
                    df_view.append({
                        'LOCAL': m.get('local', 'N/A'),
                        'CUOTA L': m.get('cuota_local', 'N/A'),
                        'VISITANTE': m.get('visitante', 'N/A'),
                        'CUOTA V': m.get('cuota_visitante', 'N/A')
                    })
                st.dataframe(pd.DataFrame(df_view), hide_index=True)

            st.divider()
            st.subheader("3. Análisis con datos REALES 2026")

            all_analisis = []
            
            for match in matches:
                home = match.get('local', '')
                away = match.get('visitante', '')
                
                odds_captura = {
                    'local': american_to_decimal(match.get('cuota_local', '')),
                    'draw': american_to_decimal(match.get('cuota_empate', '')),
                    'away': american_to_decimal(match.get('cuota_visitante', ''))
                }
                
                with st.expander(f" {home} vs {away}", expanded=True):
                    analisis = components['analyzer'].analyze_match(home, away, odds_captura)
                    all_analisis.append(analisis)
                    
                    st.caption(f" Odds mercado: Local {analisis['odds_reales']['cuota_local']:.2f} | "
                              f"Empate {analisis['odds_reales']['cuota_empate']:.2f} | "
                              f"Visitante {analisis['odds_reales']['cuota_visitante']:.2f}")
                    
                    col_p1, col_p2, col_p3 = st.columns(3)
                    with col_p1:
                        st.metric("Gana Local", f"{analisis['elo_probs']['home']:.1%}")
                    with col_p2:
                        st.metric("Empate", f"{analisis['elo_probs']['draw']:.1%}")
                    with col_p3:
                        st.metric("Gana Visitante", f"{analisis['elo_probs']['away']:.1%}")
                    
                    if analisis['value_bets']:
                        st.markdown("###  VALUE BETS DETECTADOS")
                        for vb in analisis['value_bets']:
                            col_v1, col_v2, col_v3 = st.columns(3)
                            with col_v1:
                                st.metric("Mercado", vb['name'])
                            with col_v2:
                                st.metric("Prob", f"{vb['prob']:.1%}")
                            with col_v3:
                                st.metric("EV", f"+{vb['ev']:.1%}")
                    else:
                        st.info("ℹ No se detectaron value bets significativos")

            if len(all_analisis) >= 2:
                st.divider()
                st.subheader(" MEJOR PARLAY RECOMENDADO")
                
                best_parlay = components['analyzer'].find_best_parlay(all_analisis, max_size=3)
                
                if best_parlay and best_parlay.get('picks'):
                    prob_total = np.prod([p['prob'] for p in best_parlay['picks']])
                    odds_total = np.prod([p['odds'] for p in best_parlay['picks']])
                    ev_total = (prob_total * odds_total) - 1
                    
                    col_r1, col_r2, col_r3 = st.columns(3)
                    with col_r1:
                        st.metric("Probabilidad", f"{prob_total:.1%}")
                    with col_r2:
                        st.metric("Cuota total", f"{odds_total:.2f}")
                    with col_r3:
                        st.metric("EV total", f"{ev_total:.1%}")
                    
                    st.markdown("**Selecciones:**")
                    for pick in best_parlay['picks']:
                        st.markdown(f" {pick['match']}: **{pick['selection']}** ({pick['prob']:.1%})")
                    
                    if ev_total > 0:
                        stake = (ev_total / (odds_total - 1)) * 0.25 * bankroll
                        st.success(f" Stake sugerido: ")
                else:
                    st.info("No se encontró parlay con EV positivo")

if __name__ == "__main__":
    main()
