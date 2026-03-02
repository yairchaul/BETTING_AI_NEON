import streamlit as st
import pandas as pd
from modules.ocr_reader import ImageParser
from modules.analyzer import MatchAnalyzer
from modules.parlay_builder import show_parlay_options

st.set_page_config(page_title="Analizador de Partidos IA", layout="wide")

@st.cache_resource
def init_components():
    return {
        'parser': ImageParser(),
        'analyzer': MatchAnalyzer(st.secrets.get("FOOTBALL_API_KEY", ""))
    }

components = init_components()

def main():
    st.title("🎯 Analizador Universal de Partidos")
    st.markdown("Sube una captura y analizo **partido por partido**")
    
    with st.sidebar:
        st.header("⚙️ Configuración")
        prob_minima = st.slider("Probabilidad mínima", 0.0, 1.0, 0.5, 0.05)
        
        if st.secrets.get("FOOTBALL_API_KEY"):
            st.success("✅ API conectada")
        else:
            st.warning("⚠️ Modo simulación")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Sube tu captura")
        uploaded_file = st.file_uploader("Selecciona imagen", type=['png', 'jpg', 'jpeg'])
        if uploaded_file:
            st.image(uploaded_file, use_column_width=True)
    
    if uploaded_file:
        with st.spinner("🔍 Procesando imagen..."):
            matches = components['parser'].parse_image(uploaded_file)
            st.write("Texto detectado:", matches.get('raw_text', '')[:200] if isinstance(matches, dict) else '')
            matches = matches if isinstance(matches, list) else matches.get('matches', [])
        
        if matches:
            with col2:
                st.subheader(f"2. Partidos detectados ({len(matches)})")
                df = pd.DataFrame(matches)
                st.dataframe(df, use_container_width=True)
            
            st.divider()
            st.subheader("3. Análisis por partido")
            
            all_picks = []
            for i, match in enumerate(matches):
                with st.expander(f"📊 {match['local']} vs {match['visitante']}", expanded=i==0):
                    analysis = components['analyzer'].analyze_match(
                        match['local'], match['visitante'], match.get('liga', '')
                    )
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if analysis.get('home_found'):
                            st.success(f"✅ {analysis['home_team']}")
                        else:
                            st.warning(f"⚠️ {match['local']}")
                    
                    with col_b:
                        if analysis.get('away_found'):
                            st.success(f"✅ {analysis['away_team']}")
                        else:
                            st.warning(f"⚠️ {match['visitante']}")
                    
                    markets = [m for m in analysis['markets'] if m['prob'] >= prob_minima]
                    
                    if markets:
                        market_df = pd.DataFrame([
                            {'Mercado': m['name'], 'Probabilidad': f"{m['prob']:.1%}"}
                            for m in markets[:8]
                        ])
                        st.dataframe(market_df, use_container_width=True)
                        
                        best = markets[0]
                        st.success(f"✨ Mejor: {best['name']} - {best['prob']:.1%}")
                        
                        all_picks.append({
                            'match': f"{analysis['home_team']} vs {analysis['away_team']}",
                            'selection': best['name'],
                            'prob': best['prob']
                        })
                    else:
                        st.info("Sin mercados con probabilidad suficiente")
            
            if all_picks:
                show_parlay_options(all_picks)
        else:
            st.error("❌ No se detectaron partidos")
    else:
        st.info("👆 Sube una imagen para comenzar")

if __name__ == "__main__":
    main()
