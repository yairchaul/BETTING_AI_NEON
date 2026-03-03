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
        """Procesa la imagen y extrae palabras con coordenadas"""
        if not self.client:
            return []
        
        try:
            image = vision.Image(content=image_bytes)
            response = self.client.document_text_detection(image=image)
            
            if not response.text_annotations:
                return []
            
            # Extraer cada palabra con sus coordenadas
            words_with_coords = []
            for annotation in response.text_annotations[1:]:  # Saltar el primer elemento (todo el texto)
                vertices = annotation.bounding_poly.vertices
                if vertices:
                    # Calcular centro del bounding box
                    x = sum(v.x for v in vertices) / 4
                    y = sum(v.y for v in vertices) / 4
                    
                    words_with_coords.append({
                        'text': annotation.description,
                        'x': x,
                        'y': y
                    })
            
            return self._group_by_visual_structure(words_with_coords)
            
        except Exception as e:
            st.error(f"Error procesando imagen: {e}")
            return []
    
    def _group_by_visual_structure(self, words):
        """Agrupa palabras por proximidad visual"""
        words.sort(key=lambda w: w['y'])
        
        lines = []
        current_line = [words[0]]
        
        for word in words[1:]:
            if abs(word['y'] - current_line[-1]['y']) < 15:
                current_line.append(word)
            else:
                current_line.sort(key=lambda w: w['x'])
                lines.append(current_line)
                current_line = [word]
        lines.append(current_line)
        
        # Extraer partidos de las líneas
        matches = []
        for line in lines:
            text = ' '.join([w['text'] for w in line])
            
            # Buscar odds
            odds = re.findall(r'[+-]\d{3,4}', text)
            
            if len(odds) >= 3:
                # Limpiar texto
                clean_text = re.sub(r'[+-]\d{3,4}', '', text).strip()
                clean_text = re.sub(r'Empate', '', clean_text).strip()
                
                # Dividir en posibles equipos
                parts = clean_text.split()
                if len(parts) >= 2:
                    matches.append({
                        'home': parts[0],
                        'away': parts[-1],
                        'all_odds': odds[:3]
                    })
        
        return matches
