import streamlit as st
import re
import pandas as pd

class UFCVisionProcessor:
    # Procesador visual específico para capturas de UFC
    
    def __init__(self):
        self.patterns = {
            'fighter_odds': re.compile(r'^([A-Za-zÀ-ÿ\s\-\.]+?)([+-]\d+)$'),
            'just_odds': re.compile(r'^([+-]\d+)$'),
            'just_name': re.compile(r'^([A-Za-zÀ-ÿ\s\-\.]+)$')
        }
    
    def process_raw_text(self, raw_lines):
        # Procesa las líneas de texto crudo y estructura las peleas
        peleas = []
        
        # Limpiar líneas - eliminar caracteres especiales y espacios
        lines = []
        for line in raw_lines:
            if isinstance(line, str):
                # Limpiar la línea
                clean_line = line.strip().replace('•', '').replace('*', '').strip()
                if clean_line and not clean_line.startswith('Configuración') and not clean_line.startswith('Estadísticas'):
                    lines.append(clean_line)
        
        st.write("📝 Líneas detectadas:", lines)
        
        # Separar peleadores y odds
        fighters = []
        odds = []
        
        i = 0
        while i < len(lines):
            # Si la línea parece un nombre (no empieza con + o -)
            if not lines[i].startswith('+') and not lines[i].startswith('-'):
                # Verificar si el nombre tiene el odds pegado
                match = self.patterns['fighter_odds'].match(lines[i])
                if match:
                    fighters.append(match.group(1))
                    odds.append(match.group(2))
                else:
                    fighters.append(lines[i])
                    # El odds debería estar en la siguiente línea
                    if i + 1 < len(lines) and (lines[i+1].startswith('+') or lines[i+1].startswith('-')):
                        odds.append(lines[i+1])
                        i += 1
                    else:
                        odds.append('N/A')
            i += 1
        
        # Agrupar en peleas (cada 2 fighters forman una pelea)
        for j in range(0, len(fighters)-1, 2):
            if j + 1 < len(fighters):
                pelea = {
                    'fighter1': fighters[j],
                    'odds1': odds[j] if j < len(odds) else 'N/A',
                    'fighter2': fighters[j+1],
                    'odds2': odds[j+1] if j+1 < len(odds) else 'N/A'
                }
                peleas.append(pelea)
        
        return peleas
    
    def render_ufc_fights(self, peleas):
        # Renderiza las peleas en formato UFC
        if not peleas:
            st.warning("No se pudieron estructurar las peleas correctamente")
            return []
        
        st.success(f"✅ {len(peleas)} peleas estructuradas")
        
        # Mostrar tabla de peleas
        df = pd.DataFrame(peleas)
        st.dataframe(df, use_container_width=True)
        
        picks_totales = []
        for i, pelea in enumerate(peleas):
            with st.expander(f"**🥊 {pelea['fighter1']} vs {pelea['fighter2']}**", expanded=(i == 0)):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"### 🏠 **{pelea['fighter1']}**")
                    st.metric("Cuota", pelea['odds1'])
                with col2:
                    st.markdown(f"### 🚀 **{pelea['fighter2']}**")
                    st.metric("Cuota", pelea['odds2'])
                
                # Aquí iría el cálculo de probabilidades
                # Por ahora, picks de ejemplo
                picks_totales.append({
                    'pelea': f"{pelea['fighter1']} vs {pelea['fighter2']}",
                    'favorito': pelea['fighter1'] if int(pelea['odds1']) < int(pelea['odds2']) else pelea['fighter2'],
                    'prob_favorito': 0.65  # Placeholder
                })
        
        return picks_totales
