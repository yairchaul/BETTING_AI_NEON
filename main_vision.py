"""
Main Vision - Punto de entrada de la aplicación
"""
import streamlit as st
import pandas as pd
from pathlib import Path

# Importar visuales
from visual_futbol import VisualFutbol, render_futbol
from visual_nba import VisualNBA
from visual_ufc import VisualUFC

# Importar procesadores
from processors.vision_reader import VisionReader

# Configuración de página
st.set_page_config(
    page_title="BETTING_AI - Vision Reader",
    page_icon="🎯",
    layout="wide"
)

class PickTracker:
    """Trackea los picks seleccionados"""
    def __init__(self):
        if 'picks' not in st.session_state:
            st.session_state.picks = []
    
    def agregar_pick(self, pick):
        st.session_state.picks.append(pick)
    
    def eliminar_pick(self, idx):
        if idx < len(st.session_state.picks):
            st.session_state.picks.pop(idx)
    
    def get_picks(self):
        return st.session_state.picks
    
    def limpiar(self):
        st.session_state.picks = []

def main():
    st.title("🎯 BETTING_AI - Vision Reader")
    st.markdown("---")
    
    # Sidebar - Configuración
    with st.sidebar:
        st.header("⚙️ Configuración")
        deporte = st.selectbox(
            "Selecciona deporte",
            ["Fútbol", "NBA", "UFC"]
        )
        
        st.markdown("---")
        st.header("📊 Estadísticas")
        
        # Tracker de picks
        tracker = PickTracker()
        picks = tracker.get_picks()
        st.metric("Parlays", len(picks))
        
        if st.button("🧹 Limpiar picks"):
            tracker.limpiar()
            st.rerun()
        
        st.markdown("---")
        st.header("📁 Capturas")
        
        # Listar capturas disponibles
        capturas = list(Path(".").glob("*.png")) + list(Path(".").glob("*.jpg"))
        if capturas:
            captura_seleccionada = st.selectbox(
                "Selecciona captura",
                [c.name for c in capturas]
            )
            
            if st.button("🔍 Procesar captura"):
                with st.spinner("Procesando..."):
                    vision = VisionReader()
                    eventos = vision.procesar_captura(captura_seleccionada)
                    st.session_state.eventos = eventos
                    st.success(f"✅ {len(eventos)} eventos detectados")
        else:
            st.info("No hay capturas en el directorio")
    
    # Main content
    if 'eventos' in st.session_state and st.session_state.eventos:
        for idx, evento in enumerate(st.session_state.eventos):
            # Dispatcher según deporte
            if evento.deporte == "FUTBOL":
                render_futbol(evento, idx, tracker)
            elif evento.deporte == "NBA":
                # Placeholder para NBA
                st.info(f"NBA: {evento}")
            elif evento.deporte == "UFC":
                # Placeholder para UFC
                st.info(f"UFC: {evento}")
    else:
        st.info("👈 Selecciona una captura en el sidebar para comenzar")

if __name__ == "__main__":
    main()
