import streamlit as st
import re
import pandas as pd

class UFCVisionProcessor:
    # Procesador visual específico para capturas de UFC
    
    def process_raw_text(self, raw_lines):
        # Procesa las líneas de texto crudo y estructura las peleas
        peleas = []
        
        # Limpiar y filtrar líneas
        lines = []
        for line in raw_lines:
            if isinstance(line, str):
                clean = line.strip().replace('•', '').replace('*', '').strip()
                if clean and len(clean) > 1 and not clean.startswith('Configuración') and not clean.startswith('Estadísticas'):
                    lines.append(clean)
        
        st.write("📝 Líneas detectadas:", lines)
        
        # Separar peleadores y odds
        fighters = []
        odds = []
        
        i = 0
        while i < len(lines):
            current = lines[i]
            
            # Si la línea actual parece un nombre (no empieza con + o -)
            if not current.startswith('+') and not current.startswith('-'):
                # Verificar si el nombre y odds están juntos
                match = re.search(r'^([A-Za-zÀ-ÿ\s\.]+)([+-]\d+)$', current)
                if match:
                    fighters.append(match.group(1).strip())
                    odds.append(match.group(2))
                else:
                    fighters.append(current)
                    # El odds debería estar en la siguiente línea
                    if i + 1 < len(lines) and (lines[i+1].startswith('+') or lines[i+1].startswith('-')):
                        odds.append(lines[i+1])
                        i += 1
                    else:
                        odds.append('N/A')
            i += 1
        
        # Depuración
        st.write("👤 Peleadores detectados:", fighters)
        st.write("💰 Odds detectados:", odds)
        
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
        if not peleas:
            st.warning("No se pudieron estructurar las peleas correctamente")
            return []
        
        st.success(f"✅ {len(peleas)} peleas estructuradas")
        
        # Mostrar en formato tabular
        df = pd.DataFrame(peleas)
        st.dataframe(df, use_container_width=True)
        
        # Mostrar cada pelea con su análisis
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
                    prob_favorito = 1 / (1 + 10 ** ((min(odds1, odds2) if min(odds1, odds2) > 0 else 100) / 400))
                    st.info(f"⭐ **Favorito:** {favorito} ({prob_favorito:.1%} probabilidad implícita)")
                except:
                    pass
