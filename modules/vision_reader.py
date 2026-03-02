import re
import streamlit as st
from google.cloud import vision

class ImageParser:
    def __init__(self):
        try:
            # Usamos los secretos de Streamlit para la conexión
            self.client = vision.ImageAnnotatorClient.from_service_account_info(
                dict(st.secrets["google_credentials"])
            )
        except Exception as e:
            st.error(f"Error inicializando Google Vision: {e}")
            self.client = None

    def process_image(self, image_bytes):
        """Procesa la imagen y extrae pares de equipos"""
        if not self.client: return []
        
        image = vision.Image(content=image_bytes)
        response = self.client.text_detection(image=image)
        texts = response.text_annotations

        if not texts: return []

        # El primer elemento (index 0) es TODO el texto detectado
        full_text = texts[0].description
        return self.smart_parse(full_text)

    def smart_parse(self, text):
        """Lógica para extraer equipos ignorando ruido de cuotas y fechas"""
        lines = text.split('\n')
        matches = []
        
        # 1. Limpiamos líneas que son solo números o fechas (Ruido de Caliente/Codere)
        clean_lines = []
        for line in lines:
            line = line.strip()
            # Ignorar si es solo una cuota (ej: +120, -110, 2.50)
            if re.match(r'^[+-]?\d+[.,]?\d*$', line): continue
            # Ignorar si es solo una hora o fecha corta (ej: 12:00, 02 Mar)
            if re.match(r'^\d{2}:\d{2}$', line): continue
            if re.match(r'^\d{1,2}\s+[A-Za-z]{3}', line): continue
            # Ignorar palabras de control de la app
            if line.lower() in ['empate', 'vs', 'v', 'cerrar', 'apuesta', 'mis']: continue
            
            if len(line) > 2:
                clean_lines.append(line)

        # 2. Agrupamos por pares (Local vs Visitante)
        # Las apps de apuestas suelen poner: Equipo A \n Equipo B \n Cuotas...
        i = 0
        while i < len(clean_lines) - 1:
            local = clean_lines[i]
            visitante = clean_lines[i+1]
            
            # Si el "visitante" parece otro equipo y no basura, los unimos
            if self.is_valid_team_pair(local, visitante):
                matches.append({
                    "home": self.fix_common_names(local),
                    "away": self.fix_common_names(visitante)
                })
                i += 2 # Saltamos el par
            else:
                i += 1
                
        return matches

    def is_valid_team_pair(self, t1, t2):
        """Valida que no estemos emparejando un equipo con un nombre de liga o botón"""
        bad_words = ['liga', 'champions', 'premier', 'apuesta', 'vivo', 'finalizado']
        combined = (t1 + t2).lower()
        return not any(word in combined for word in bad_words)

    def fix_common_names(self, name):
        """Corrige nombres que el OCR a veces corta o confunde"""
        name = name.replace('|', '').strip()
        # Mapeo de nombres cortos a largos para que tu cerebro.py los encuentre
        corrections = {
            "PSG": "Paris Saint Germain",
            "M'gladbach": "Borussia Monchengladbach",
            "U. Berlin": "Union Berlin",
            "Le Havre AC": "Le Havre"
        }
        return corrections.get(name, name)

def procesar_texto_manual(texto):
    """Función de apoyo para la caja de texto manual"""
    lineas = texto.split('\n')
    partidos = []
    for linea in lineas:
        if ' vs ' in linea.lower():
            teams = re.split(r' vs ', linea, flags=re.IGNORECASE)
            if len(teams) == 2:
                partidos.append({"home": teams[0].strip(), "away": teams[1].strip()})
    return partidos
