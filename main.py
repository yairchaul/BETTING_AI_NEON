import streamlit as st
import pandas as pd
import re
from modules.vision_reader import ImageParser
from modules.analyzer import MatchAnalyzer
from modules.parlay_builder import show_parlay_options
from modules.betting_tracker import BettingTracker
from modules.team_matcher import TeamMatcher
from modules.montecarlo import run_simulation

st.set_page_config(page_title="Analizador de Partidos IA", layout="wide")

@st.cache_resource
def init_components():
    """Inicializa componentes con cache para mejorar rendimiento"""
    return {
        'vision': ImageParser(),
        'analyzer': MatchAnalyzer(st.secrets.get("FOOTBALL_API_KEY", "")),
        'tracker': BettingTracker(),
        'matcher': TeamMatcher(st.secrets.get("FOOTBALL_API_KEY", ""))
    }

components = init_components()

def main():
    st.title("🎯 Analizador Universal de Partidos")
    st.markdown("Sube una captura y analizo **partido por partido**")
    
    # ============================================================================
    # SIDEBAR CON CONFIGURACIÓN AVANZADA
    # ============================================================================
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        prob_minima = st.slider(
            "Probabilidad mínima", 
            min_value=0.0, 
            max_value=1.0, 
            value=0.5, 
            step=0.05,
            help="Solo muestra mercados con probabilidad mayor a este valor"
        )
        
        st.divider()
        
        st.subheader("🎲 Mercados a mostrar")
        categorias = st.multiselect(
            "Selecciona categorías",
            ["1X2", "Doble Oportunidad", "Totales", "Primer Tiempo", 
             "BTTS", "Handicap", "Goleador", "Combinado", "Totales (Especial)"],
            default=["1X2", "Totales", "Primer Tiempo", "BTTS", "Totales (Especial)"],
            help="Selecciona qué tipos de mercados quieres ver"
        )
        
        show_high_scoring = st.checkbox(
            "⚽ Enfatizar equipos goleadores", 
            value=True,
            help="Resalta mercados de Over 4.5 y Over 5.5 goles"
        )
        
        st.divider()
        
        if st.secrets.get("FOOTBALL_API_KEY"):
            st.success("✅ API conectada")
        else:
            st.warning("⚠️ Modo simulación")
        
        debug_mode = st.checkbox("🔧 Mostrar debug OCR", value=True)
        components['tracker'].show_tracker_ui()
    
    # ============================================================================
    # ÁREA PRINCIPAL
    # ============================================================================
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Sube tu captura")
        uploaded_file = st.file_uploader(
            "Selecciona imagen", 
            type=['png', 'jpg', 'jpeg'],
            help="Sube una captura de pantalla con partidos y cuotas"
        )
        
        if uploaded_file:
            st.image(uploaded_file, caption="Imagen subida", use_container_width=True)
    
    if uploaded_file:
        # --- NUEVA LÓGICA DE PROCESAMIENTO COMPATIBLE ---
        with st.spinner("🔍 Procesando imagen con Google Vision..."):
            img_bytes = uploaded_file.read()
            # Llamamos al nuevo método process_image de tu vision_reader.py
            matches = components['vision'].process_image(img_bytes)
            
            # Detección opcional de "En Vivo" (basado en el texto raw)
            # Intentamos obtener el texto crudo para ver si hay marcadores (1-0) o minutos (45')
            raw_text = ""
            try:
                # Esto asume que tu vision_reader guarda el último resultado o permite acceso al cliente
                response = components['vision'].client.text_detection(image={'content': img_bytes})
                raw_text = response.text_annotations[0].description
                if re.search(r"\d+'", raw_text) or re.search(r"\d\s*-\s*\d", raw_text):
                    st.info("🏟️ **Partido en tiempo real detectado.** Analizando bajo condiciones de juego.")
            except:
                pass
        
        # --- MOSTRAR DEBUG ---
        if debug_mode:
            with st.expander("🔧 Debug OCR"):
                st.write(f"Partidos detectados: {len(matches)}")
                if raw_text: st.text(raw_text[:500])
        
        if matches:
            with col2:
                st.subheader(f"2. Partidos detectados ({len(matches)})")
                df_data = []
                for m in matches:
                    df_data.append({
                        'Local': m['home'],
                        'Visitante': m['away']
                    })
                st.dataframe(pd.DataFrame(df_data), use_container_width=True)
            
            st.divider()
            st.subheader("3. Análisis partido por partido")
            
            all_picks = []
            for i, match in enumerate(matches):
                home = match['home']
                away = match['away']
                
                with st.expander(f"📊 {home} vs {away}", expanded=i==0):
                    analysis = components['analyzer'].analyze_match(home, away, "")
                    
                    # Mostrar resultados de búsqueda
                    col_a, col_b = st.columns(2)
                    col_a.write(f"🏠 {analysis['home_team']} " + ("✅" if analysis.get('home_found') else "❓"))
                    col_b.write(f"🚀 {analysis['away_team']} " + ("✅" if analysis.get('away_found') else "❓"))
                    
                    # Filtrar mercados
                    markets_filtered = [
                        m for m in analysis['markets'] 
                        if m['prob'] >= prob_minima and m['category'] in categorias
                    ]
                    
                    if markets_filtered:
                        st.caption(f"📊 Goles promedio: {analysis['probabilidades']['goles_promedio']:.2f}")
                        
                        market_df = pd.DataFrame([{
                            'Mercado': m['name'],
                            'Probabilidad': f"{m['prob']:.1%}",
                            'Categoría': m['category']
                        } for m in markets_filtered[:10]])
                        
                        st.dataframe(market_df, use_container_width=True, hide_index=True)
                        
                        best = markets_filtered[0]
                        st.success(f"✨ **Mejor opción:** {best['name']} - {best['prob']:.1%}")
                        
                        all_picks.append({
                            'match': f"{home} vs {away}",
                            'selection': best['name'],
                            'prob': best['prob'],
                            'category': best['category']
                        })
            
            if all_picks:
                show_parlay_options(all_picks, components['tracker'])
        else:
            st.error("❌ No se detectaron partidos. Intenta con una imagen más clara.")

if __name__ == "__main__":
    main()
