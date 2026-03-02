# main.py
import streamlit as st
import pandas as pd
import re
from modules.vision_reader import ImageParser
from modules.analyzer import MatchAnalyzer
from modules.betting_tracker import BettingTracker
from modules.ev_engine import build_smart_parlay

st.set_page_config(page_title="Analizador de Partidos IA", layout="wide")

@st.cache_resource
def init_components():
    return {
        'vision': ImageParser(),
        'analyzer': MatchAnalyzer(st.secrets.get("FOOTBALL_API_KEY", "")),
        'tracker': BettingTracker()
    }

components = init_components()

def main():
    st.title("🎯 Analizador Universal de Partidos")
    
    # --- CONFIGURACIÓN SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Configuración")
        prob_minima = st.slider("Probabilidad mínima", 0.0, 1.0, 0.5, 0.05)
        monto_apuesta = st.number_input("💰 Monto a invertir ($)", value=100.0, step=10.0)
        categorias = st.multiselect("Mercados", ["1X2", "BTTS", "Totales", "Primer Tiempo"], default=["1X2", "Totales"])
        debug_mode = st.checkbox("🔧 Mostrar debug OCR", value=True)
        components['tracker'].show_tracker_ui()

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Sube tu captura")
        uploaded_file = st.file_uploader("Selecciona imagen", type=['png', 'jpg', 'jpeg'])
        if uploaded_file:
            st.image(uploaded_file, use_container_width=True)

    if uploaded_file:
        with st.spinner("🔍 Analizando filas y equipos..."):
            img_bytes = uploaded_file.getvalue()
            matches = components['vision'].process_image(img_bytes)

        if matches:
            with col2:
                st.subheader(f"2. Partidos detectados ({len(matches)})")
                df_data = []
                for m in matches:
                    df_data.append({
                        'Local': m['home'],
                        'Visitante': m['away'],
                        'L': m['all_odds'][0],
                        'E': m['all_odds'][1],
                        'V': m['all_odds'][2]
                    })
                st.table(df_data) # Usamos table para una vista más clara de verificación

            # --- ANÁLISIS Y PARLAYS ---
            st.divider()
            all_picks_for_ev = []
            
            for i, match in enumerate(matches):
                with st.expander(f"📊 {match['home']} vs {match['away']}", expanded=(i==0)):
                    analysis = components['analyzer'].analyze_match(match['home'], match['away'], "")
                    
                    # Filtrar y mostrar mejores picks
                    markets = [m for m in analysis['markets'] if m['prob'] >= prob_minima]
                    if markets:
                        st.write(f"✅ Recomendación: {markets[0]['name']} ({markets[0]['prob']:.1%})")
                        # Agregar al motor EV (aquí podrías convertir cuotas americanas a decimales)
                        all_picks_for_ev.append({
                            'match': f"{match['home']} vs {match['away']}",
                            'selection': markets[0]['name'],
                            'probability': markets[0]['prob'],
                            'odd': 2.0, # Valor por defecto si la cuota es N/A
                            'ev': 0.1,
                            'category': markets[0]['category']
                        })

            # --- SECCIÓN DE GANANCIAS (LO QUE TE GUSTABA) ---
            if all_picks_for_ev:
                st.header("🔥 Parlay Maestro Sugerido")
                smart_parlay = build_smart_parlay(all_picks_for_ev)
                
                if smart_parlay:
                    c1, c2, c3 = st.columns(3)
                    cuota_final = smart_parlay['total_odd']
                    pago_total = monto_apuesta * cuota_final
                    
                    c1.metric("Cuota Total", f"{cuota_final:.2f}")
                    c2.metric("Pago Estimado", f"${pago_total:.2f}")
                    c3.metric("Ganancia Neta", f"${(pago_total - monto_apuesta):.2f}", delta="ROI Positivo")
                    
                    for m in smart_parlay['matches']:
                        st.write(f"✔️ {m}")

        else:
            st.error("No se detectaron pares de equipos. Intenta con una captura más nítida.")

if __name__ == "__main__":
    main()
