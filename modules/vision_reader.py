# modules/vision_reader.py
import re
import streamlit as st
from google.cloud import vision

class ImageParser:
    def __init__(self):
        """Inicializa el cliente de Google Vision"""
        try:
            self.client = vision.ImageAnnotatorClient.from_service_account_info(
                dict(st.secrets["google_credentials"])
            )
        except Exception as e:
            st.error(f"Error inicializando Google Vision: {e}")
            self.client = None

    def process_image(self, image_bytes):
        """Procesa la imagen y extrae pares de equipos"""
        if not self.client:
            return []
        
        try:
            image = vision.Image(content=image_bytes)
            response = self.client.text_detection(image=image)
            texts = response.text_annotations

            if not texts:
                return []

            full_text = texts[0].description
            return self.smart_parse(full_text)
        except Exception as e:
            st.error(f"Error procesando imagen: {e}")
            return []

    def smart_parse(self, text):
        """
        Interpreta la estructura de tabla de 3 columnas:
        Col1: Equipos Locales
        Col2: Cuotas Locales
        Col3: Palabra "Empate"
        Col4: Cuotas Empate
        Col5: Equipos Visitantes
        Col6: Cuotas Visitantes
        """
        lines = text.split('\n')
        
        # Clasificar líneas por su contenido
        equipos_locales = []
        cuotas_locales = []
        empates = []
        cuotas_empate = []
        equipos_visitantes = []
        cuotas_visitantes = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detectar si es un equipo (letras, sin números al inicio)
            if re.match(r'^[A-Za-z]', line) and not re.search(r'[+-]\d', line):
                if "Empate" not in line and len(line) > 2:
                    # Determinar si es local o visitante basado en el contexto
                    # Por ahora, los primeros 5 son locales, los últimos 5 son visitantes
                    if len(equipos_locales) < 5:
                        equipos_locales.append(line)
                    else:
                        equipos_visitantes.append(line)
            
            # Detectar cuotas (+/- números)
            elif re.match(r'[+-]\d{3,4}', line):
                if len(cuotas_locales) < 5:
                    cuotas_locales.append(line)
                elif len(cuotas_empate) < 5:
                    cuotas_empate.append(line)
                else:
                    cuotas_visitantes.append(line)
            
            # Detectar la palabra "Empate"
            elif "Empate" in line:
                empates.append(line)
        
        # Debug para ver cómo se clasificó
        st.write("**Clasificación de líneas:**")
        st.write(f"Locales: {equipos_locales}")
        st.write(f"Cuotas Locales: {cuotas_locales}")
        st.write(f"Cuotas Empate: {cuotas_empate}")
        st.write(f"Visitantes: {equipos_visitantes}")
        st.write(f"Cuotas Visitantes: {cuotas_visitantes}")
        
        # Construir matches
        matches = []
        for i in range(min(len(equipos_locales), len(equipos_visitantes))):
            if i < len(cuotas_locales) and i < len(cuotas_empate) and i < len(cuotas_visitantes):
                matches.append({
                    "home": equipos_locales[i],
                    "away": equipos_visitantes[i],
                    "all_odds": [
                        cuotas_locales[i],
                        cuotas_empate[i],
                        cuotas_visitantes[i]
                    ]
                })
        
        return matches

    def is_team_name(self, text):
        """Determina si un texto es probable nombre de equipo"""
        if not text or len(text) < 2:
            return False
        
        text_lower = text.lower()
        
        # Palabras que definitivamente NO son equipos
        forbidden = ['empate', 'draw', 'vs', 'v', 'apuesta', 'cuota', 'resultado', 
                     'final', 'vivo', 'directo', 'hoy', 'mañana', 'score', 'points',
                     'liga', 'champions', 'premier', 'calendar', 'schedule']
        
        if any(word in text_lower for word in forbidden):
            return False
        
        # No debe ser un número
        if re.match(r'^[+-]?\d+$', text):
            return False
        
        return True

    def fix_common_names(self, name):
        """Corrige nombres que el OCR a veces corta o confunde"""
        name = name.replace('|', '').strip()
        
        # Correcciones comunes
        corrections = {
            "RCD Mallorca": "RCD Mallorca",
            "Real Oviedo": "Real Oviedo",
            "Getafe": "Getafe",
            "Girona": "Girona",
            "Real Madrid": "Real Madrid",
            "Rayo Vallecano": "Rayo Vallecano",
            "Celta de Vigo": "Celta de Vigo",
            "Osasuna": "Osasuna",
            "Levante": "Levante"
        }
        
        return corrections.get(name, name)


# Función de respaldo para entrada manual
def procesar_texto_manual(texto):
    """Procesa texto ingresado manualmente"""
    lineas = texto.split('\n')
    partidos = []
    for linea in lineas:
        if ' vs ' in linea.lower():
            teams = re.split(r' vs ', linea, flags=re.IGNORECASE)
            if len(teams) == 2:
                partidos.append({
                    "home": teams[0].strip(), 
                    "away": teams[1].strip(),
                    "all_odds": ['N/A', 'N/A', 'N/A']
                })
    return partidos
