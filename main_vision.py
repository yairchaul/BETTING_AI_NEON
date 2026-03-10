import streamlit as st
import pandas as pd
from datetime import datetime
from modules.vision_reader import ImageParser
from sports.ufc.vision_processor import UFCVisionProcessor
from sports.nba.vision_processor import NBAVisionProcessor
from sports.soccer.vision_processor import SoccerVisionProcessor
from sports.ufc import UFCProcessor
from sports.nba import NBAProcessor
from sports.soccer import SoccerProcessor

st.set_page_config(page_title='BETTING_AI', page_icon='🎯', layout='wide')

class ParlayTracker:
    def __init__(self):
        self.parlays = []
        self.current_picks = []
    
    def add_pick(self, partido, mercado, prob, nivel, deporte, ev=0):
        self.current_picks.append({
            'partido': partido,
            'mercado': mercado,
            'prob': prob,
            'nivel': nivel,
            'deporte': deporte,
            'ev': ev
        })
    
    def clear_picks(self):
        self.current_picks = []
    
    def build_parlay(self):
        if len(self.current_picks) < 2:
            return None
        prob_total = 1.0
        ev_total = 0.0
        for pick in self.current_picks:
            prob_total *= pick['prob']
            ev_total += pick['ev']
        return {'picks': self.current_picks.copy(), 'prob_total': prob_total, 'ev_total': ev_total}
    
    def get_stats(self):
        return {'total': len(self.parlays)}

def main():
    st.title('🎯 BETTING_AI - Analizador por Deportes')
    st.caption(f'📅 {datetime.now().strftime("%d/%m/%Y %H:%M")}')
    
    tracker = ParlayTracker()
    vision = ImageParser()
    
    # Procesadores de análisis
    ufc_processor = UFCProcessor()
    nba_processor = NBAProcessor()
    soccer_processor = SoccerProcessor()
    
    # Procesadores visuales
    ufc_vision = UFCVisionProcessor()
    nba_vision = NBAVisionProcessor()
    soccer_vision = SoccerVisionProcessor()
    
    with st.sidebar:
        st.header('⚙️ Configuración')
        deporte = st.radio(
            'Selecciona deporte',
            ['⚽ Fútbol', '🏀 NBA', '🥊 UFC'],
            index=0
        )
        
        st.divider()
        st.header('📊 Estadísticas')
        st.metric('Parlays', tracker.get_stats()['total'])
        if st.button('🧹 Limpiar picks'):
            tracker.clear_picks()
            st.rerun()
    
    st.header(f"📸 Sube tu captura de {deporte}")
    uploaded = st.file_uploader(
        "Selecciona una imagen",
        type=['png','jpg','jpeg'],
        key=f"uploader_{deporte}"
    )
    
    if uploaded:
        st.image(uploaded, caption='Captura subida', use_container_width=True)
        
        with st.spinner(f'🔍 Analizando imagen...'):
            img_bytes = uploaded.getvalue()
            matches = vision.process_image(img_bytes)
            
            # Extraer texto de matches
            texto_crudo = []
            if matches:
                for match in matches:
                    if isinstance(match, dict):
                        for key, value in match.items():
                            if isinstance(value, str):
                                texto_crudo.append(value)
                            elif isinstance(value, list):
                                texto_crudo.extend([str(v) for v in value])
                    elif isinstance(match, str):
                        texto_crudo.append(match)
            
            # =========================================
            # PROCESAMIENTO ESPECÍFICO POR DEPORTE
            # =========================================
            
            if deporte == '🥊 UFC':
                st.header('🥊 Análisis UFC')
                
                # Mostrar texto detectado para depuración
                with st.expander("🔍 Ver texto detectado"):
                    st.write(texto_crudo)
                
                # Procesar con el vision processor de UFC
                peleas = ufc_vision.process_raw_text(texto_crudo)
                if peleas:
                    # Renderizar peleas
                    for i, pelea in enumerate(peleas):
                        with st.expander(f"**🥊 {pelea['fighter1']} vs {pelea['fighter2']}**", expanded=(i == 0)):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"### 🏠 **{pelea['fighter1']}**")
                                st.metric("Cuota", pelea['odds1'])
                            with col2:
                                st.markdown(f"### 🚀 **{pelea['fighter2']}**")
                                st.metric("Cuota", pelea['odds2'])
                            
                            # Determinar favorito
                            try:
                                odds1 = int(pelea['odds1'])
                                odds2 = int(pelea['odds2'])
                                favorito = pelea['fighter1'] if odds1 < odds2 else pelea['fighter2']
                                prob_impl = 1 / (1 + 10 ** ((min(abs(odds1), abs(odds2)) if min(odds1, odds2) > 0 else 100) / 400))
                                st.info(f"⭐ **Favorito:** {favorito} ({prob_impl:.1%} probabilidad)")
                            except:
                                pass
                            
                            # Botón para agregar al parlay
                            if st.button(f"➕ Agregar {favorito if 'favorito' in locals() else 'pelea'}", key=f"ufc_{i}"):
                                tracker.add_pick(
                                    f"{pelea['fighter1']} vs {pelea['fighter2']}",
                                    f"Gana {favorito}" if 'favorito' in locals() else "Pelea",
                                    0.65,  # Placeholder
                                    1,
                                    'UFC'
                                )
                                st.rerun()
                else:
                    st.error('❌ No se detectaron peleas en la imagen')
            
            elif deporte == '🏀 NBA':
                st.header('🏀 Análisis NBA')
                st.info('🔧 Procesador NBA en desarrollo')
            
            else:  # Fútbol
                st.header('⚽ Análisis Fútbol')
                # Usar el render_match existente
                for i, match in enumerate(matches):
                    odds = match.get('all_odds', ['N/A', 'N/A', 'N/A'])
                    picks = soccer_processor.render_match(
                        i,
                        match.get('home', 'Local'),
                        match.get('away', 'Visitante'),
                        odds
                    )
                    for p in picks:
                        if st.button(f"➕ {p['mercado']}", key=f"futbol_{i}_{p['nivel']}"):
                            tracker.add_pick(
                                f"{match.get('home', 'Local')} vs {match.get('away', 'Visitante')}",
                                p['mercado'], p['prob'], p['nivel'], 'Fútbol',
                                p.get('ev', 0)
                            )
                            st.rerun()
    
    # Parlay
    if tracker.current_picks:
        st.divider()
        st.header('🎯 Parlay en construcción')
        df = pd.DataFrame(tracker.current_picks)
        st.dataframe(df, use_container_width=True)
        
        parlay = tracker.build_parlay()
        if parlay:
            col1, col2 = st.columns(2)
            with col1:
                st.metric('Probabilidad total', f"{parlay['prob_total']:.1%}")
            with col2:
                st.metric('EV total', f"{parlay['ev_total']:.1%}")
            
            if st.button('✅ Confirmar parlay'):
                tracker.parlays.append(parlay)
                tracker.clear_picks()
                st.balloons()
                st.rerun()

if __name__ == '__main__':
    main()
