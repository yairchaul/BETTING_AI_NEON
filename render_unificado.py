"""
RENDERIZADOR UNIFICADO - Tarjetas de análisis para todos los deportes
"""
import streamlit as st

def render_analisis_card(analisis_heur, analisis_gemini=None, analisis_premium=None):
    """Renderiza una tarjeta de análisis unificada para cualquier deporte"""
    
    if not analisis_heur:
        return
    
    st.markdown("---")
    
    # HEURÍSTICO
    st.markdown("### 📊 HEURÍSTICO")
    st.write(f"**Recomendación:** {analisis_heur.get('recomendacion', 'N/A')}")
    
    confianza = analisis_heur.get('confianza', 0)
    if isinstance(confianza, (int, float)):
        st.progress(confianza / 100)
        st.caption(f"Confianza: {confianza}%")
    else:
        st.caption(f"Confianza: {confianza}")
    
    # Detalles adicionales según tipo de análisis
    if analisis_heur.get('proyeccion'):
        st.caption(f"Proyección: {analisis_heur.get('proyeccion', 'N/A')}")
    if analisis_heur.get('total_proyectado'):
        st.caption(f"Total IA: {analisis_heur.get('total_proyectado', 'N/A')}")
    if analisis_heur.get('consistencia'):
        st.caption(f"Consistencia: {analisis_heur.get('consistencia', 'N/A')}")
    if analisis_heur.get('metodo'):
        st.caption(f"Método: {analisis_heur.get('metodo', 'N/A')}")
    
    if analisis_heur.get('etiqueta_verde', False):
        st.success("🔥 PICK DE ALTA CONFIANZA")
    
    # GEMINI IA
    if analisis_gemini:
        st.markdown("### 🤖 GEMINI IA")
        st.info(str(analisis_gemini))
    
    # PREMIUM ANALYTICS
    if analisis_premium:
        st.markdown("### 🔬 PREMIUM ANALYTICS")
        if isinstance(analisis_premium, dict):
            st.write(analisis_premium.get('analisis', 'Pendiente'))
        else:
            st.write(str(analisis_premium))

def render_partido_header(titulo, subtitulo=None):
    """Renderiza el encabezado de un partido"""
    st.markdown(f"### {titulo}")
    if subtitulo:
        st.caption(subtitulo)
