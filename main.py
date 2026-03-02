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
    
    # ============================================================================
    # SIDEBAR CON CONFIGURACIÓN AVANZADA
    # ============================================================================
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Probabilidad mínima
        prob_minima = st.slider(
            "Probabilidad mínima", 
            min_value=0.0, 
            max_value=1.0, 
            value=0.5, 
            step=0.05,
            help="Solo muestra mercados con probabilidad mayor a este valor"
        )
        
        st.divider()
        
        # Filtros por categoría de mercado
        st.subheader("🎲 Mercados a mostrar")
        categorias = st.multiselect(
            "Selecciona categorías",
            ["1X2", "Doble Oportunidad", "Totales", "Primer Tiempo", 
             "BTTS", "Handicap", "Goleador", "Combinado", "Totales (Especial)"],
            default=["1X2", "Totales", "Primer Tiempo", "BTTS", "Totales (Especial)"],
            help="Selecciona qué tipos de mercados quieres ver"
        )
        
        # Opción para equipos goleadores
        show_high_scoring = st.checkbox(
            "⚽ Enfatizar equipos goleadores", 
            value=True,
            help="Resalta mercados de Over 4.5 y Over 5.5 goles"
        )
        
        st.divider()
        
        # Estado de la API
        if st.secrets.get("FOOTBALL_API_KEY"):
            st.success("✅ API conectada")
            st.caption("Buscando equipos en base de datos global")
        else:
            st.warning("⚠️ Modo simulación")
            st.caption("Agrega FOOTBALL_API_KEY a secrets para búsqueda real")
        
        # Modo debug
        debug_mode = st.checkbox("🔧 Modo debug", value=True)
    
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
            # Mostrar imagen con el nuevo parámetro
            st.image(uploaded_file, caption="Imagen subida", use_container_width=True)
    
    if uploaded_file:
        # Procesar imagen con OCR
        with st.spinner("🔍 Procesando imagen..."):
            result = components['parser'].parse_image(uploaded_file)
            matches = result['matches']
            raw_text = result['raw_text']
        
        # Mostrar texto detectado en modo debug
        if debug_mode:
            with st.expander("🔬 Ver texto detectado (debug)", expanded=True):
                st.text(raw_text)
        
        if matches:
            with col2:
                st.subheader(f"2. Partidos detectados ({len(matches)})")
                
                # Mostrar tabla de partidos detectados
                df_matches = pd.DataFrame(matches)
                st.dataframe(df_matches, use_container_width=True)
                
                # Advertencia si son datos de prueba
               if not matches:
    st.warning("⚠️ No se detectaron partidos en la imagen")
            
            st.divider()
            st.subheader("3. Análisis partido por partido")
            
            all_picks = []
            
            # Analizar cada partido detectado
            for i, match in enumerate(matches):
                with st.expander(f"📊 {match['local']} vs {match['visitante']}", expanded=i==0):
                    
                    # Analizar el partido
                    analysis = components['analyzer'].analyze_match(
                        match['local'], 
                        match['visitante'], 
                        match.get('liga', '')
                    )
                    
                    # Mostrar resultados de búsqueda de equipos
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if analysis.get('home_found'):
                            st.success(f"✅ Local: {analysis['home_team']}")
                        else:
                            st.warning(f"⚠️ Local: {match['local']} (no encontrado en API)")
                    
                    with col_b:
                        if analysis.get('away_found'):
                            st.success(f"✅ Visitante: {analysis['away_team']}")
                        else:
                            st.warning(f"⚠️ Visitante: {match['visitante']} (no encontrado en API)")
                    
                    # ====================================================================
                    # FILTRAR MERCADOS POR PROBABILIDAD Y CATEGORÍA
                    # ====================================================================
                    markets_filtered = [
                        m for m in analysis['markets'] 
                        if m['prob'] >= prob_minima and m['category'] in categorias
                    ]
                    
                    # Si show_high_scoring está activado, resaltar mercados Over 4.5+
                    if show_high_scoring:
                        for m in markets_filtered:
                            if 'Over 4.5' in m['name'] or 'Over 5.5' in m['name']:
                                m['highlight'] = True
                    
                    if markets_filtered:
                        # Mostrar estadísticas generales
                        st.caption(f"📊 Goles promedio esperados: {analysis['probabilidades']['goles_promedio']:.2f}")
                        
                        # Crear DataFrame para mostrar mercados
                        market_data = []
                        for m in markets_filtered[:15]:  # Top 15 mercados
                            highlight = "🔴 " if m.get('highlight') else ""
                            market_data.append({
                                'Mercado': highlight + m['name'],
                                'Probabilidad': f"{m['prob']:.1%}",
                                'Categoría': m['category']
                            })
                        
                        st.dataframe(
                            pd.DataFrame(market_data), 
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Mejor opción general
                        best = markets_filtered[0]
                        best_emoji = "🔴" if best.get('highlight') else "✨"
                        st.success(f"{best_emoji} **Mejor opción:** {best['name']} - {best['prob']:.1%}")
                        
                        # Guardar para parlays (solo top 3 por partido)
                        for m in markets_filtered[:3]:
                            all_picks.append({
                                'match': f"{analysis['home_team']} vs {analysis['away_team']}",
                                'selection': m['name'],
                                'prob': m['prob'],
                                'category': m['category']
                            })
                    else:
                        st.info("📭 No hay mercados con los filtros seleccionados")
                        st.caption("Prueba con una probabilidad mínima más baja o selecciona más categorías")
            
            # ====================================================================
            # GENERAR PARLAYS CON LAS MEJORES OPCIONES
            # ====================================================================
            if all_picks:
                # Limitar a picks únicos por partido (los mejores)
                unique_picks = []
                seen_matches = set()
                for pick in all_picks:
                    if pick['match'] not in seen_matches:
                        seen_matches.add(pick['match'])
                        unique_picks.append(pick)
                
                show_parlay_options(unique_picks)
            else:
                st.info("ℹ️ No hay suficientes picks para generar parlays")
        
        else:
            st.error("❌ No se detectaron partidos en la imagen")
            st.info("""
            **Sugerencias para mejorar la detección:**
            - Asegúrate que la imagen tenga buena resolución
            - Los nombres de equipos deben ser legibles
            - Activa el modo debug para ver qué texto detecta el OCR
            - Intenta con una captura más clara o de diferente formato
            """)
    
    else:
        # Mensaje inicial cuando no hay imagen
        st.info("👆 Sube una imagen para comenzar el análisis")
        
        with st.expander("📋 Ver ejemplo de formato aceptado"):
            st.code("""
Asia - Kyrgyzstan - Pervaya Liga
FC Kyrgyzaltyn vs Oshmu-Aldiyer
02 Mar 03:00
Puntos: +17

Australia - Victoria Premier League 2
Bulleen Lions vs Eltham Redbacks FC
02 Mar 03:30
Puntos: +16
            """)
        
        with st.expander("ℹ️ Cómo funciona"):
            st.markdown("""
            ### 🎯 Flujo de análisis:
            
            1. **Subes una captura** de cualquier casa de apuestas
            2. **El OCR detecta** los nombres de equipos automáticamente
            3. **Buscamos los equipos** en la base de datos global (API-Sports)
            4. **Simulamos el partido** con Monte Carlo (20,000 simulaciones)
            5. **Analizamos TODOS los mercados** posibles:
               - Resultado final (1X2)
               - Doble oportunidad
               - Totales de goles (Over 0.5 hasta Over 5.5)
               - Primer tiempo (goles y BTTS)
               - Handicaps y goleadas
               - Equipos goleadores (3+ goles)
            6. **Te mostramos la mejor opción** para cada partido
            7. **Generamos parlays** combinando las mejores selecciones
            8. **Registra tus apuestas** y lleva tracking de resultados
            
            ### 🆕 Novedades:
            - ✅ Over 5.5 goles para equipos goleadores (como PSV)
            - ✅ Over 1.5 goles en primer tiempo
            - ✅ Ambos anotan en primer tiempo
            - ✅ Filtros por categoría de mercado
            - ✅ Sistema de registro de apuestas
            """)

if __name__ == "__main__":
    main()
