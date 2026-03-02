import pytesseract
from PIL import Image
import re
import streamlit as st
import numpy as np

class ImageParser:
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
    
    def preprocess_image(self, image):
        """Mejora la imagen para mejor OCR"""
        # Convertir a array si es necesario
        if isinstance(image, Image.Image):
            # Convertir a escala de grises
            if image.mode != 'L':
                image = image.convert('L')
            
            # Aumentar contraste
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Binarización adaptativa
            image = image.point(lambda x: 0 if x < 180 else 255, '1')
        
        return image
    
    def parse_image(self, uploaded_file):
        """Procesa la imagen y extrae los partidos REALES"""
        try:
            # Leer imagen
            image = Image.open(uploaded_file)
            
            # Mostrar imagen original para debug
            st.image(image, caption="Imagen original", width=300)
            
            # Preprocesar
            processed = self.preprocess_image(image)
            
            # Mostrar imagen procesada para debug
            st.image(processed, caption="Imagen procesada para OCR", width=300)
            
            # Configuración OCR optimizada
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .-+"'
            
            # Extraer texto
            text = pytesseract.image_to_string(processed, config=custom_config)
            
            # DEBUG: Mostrar texto detectado
            st.text("Texto detectado por OCR:")
            st.code(text)
            
            # Extraer partidos del texto
            matches = self._extract_matches(text)
            
            # DEBUG: Mostrar lo que se extrajo
            st.write("Partidos extraídos:", matches)
            
            return {
                'matches': matches,
                'raw_text': text
            }
            
        except Exception as e:
            st.error(f"Error OCR: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            return {'matches': [], 'raw_text': ''}
    
    def _extract_matches(self, text):
        """Extrae partidos del texto con mejor detección"""
        matches = []
        lines = text.split('\n')
        
        # Patrones para detectar cuotas
        odds_pattern = r'[+-]?\d+\.?\d*'
        
        for line in lines:
            line = line.strip()
            if len(line) < 10:  # Ignorar líneas muy cortas
                continue
            
            # Buscar líneas con posible formato de partido
            # Patrón: Equipo + números (cuotas) + Equipo
            parts = re.split(r'\s+', line)
            
            # Buscar números que parezcan cuotas
            number_indices = [i for i, p in enumerate(parts) if re.match(odds_pattern, p)]
            
            if len(number_indices) >= 3:  # Tiene al menos 3 números (cuotas)
                # Tomar texto antes del primer número como equipo local
                if number_indices[0] > 0:
                    local = ' '.join(parts[:number_indices[0]])
                    
                    # Tomar texto después del último número como equipo visitante
                    if number_indices[-1] < len(parts) - 1:
                        visitante = ' '.join(parts[number_indices[-1]+1:])
                        
                        # Limpiar nombres
                        local = re.sub(r'[^A-Za-z\s]', '', local).strip()
                        visitante = re.sub(r'[^A-Za-z\s]', '', visitante).strip()
                        
                        if local and visitante and len(local) > 3 and len(visitante) > 3:
                            matches.append({
                                'local': local,
                                'visitante': visitante,
                                'liga': 'Detectada de imagen'
                            })
        
        # Si no encuentra con ese patrón, buscar "vs"
        if not matches:
            for line in lines:
                if ' vs ' in line.lower():
                    parts = re.split(r'\s+vs\s+', line, flags=re.IGNORECASE)
                    if len(parts) == 2:
                        matches.append({
                            'local': parts[0].strip(),
                            'visitante': parts[1].strip(),
                            'liga': 'Detectada de imagen'
                        })
        
        # NO HAY FALLBACK - si no encuentra, devuelve lista vacía
        return matches
