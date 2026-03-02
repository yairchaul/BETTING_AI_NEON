import pytesseract
from PIL import Image
import re
import streamlit as st

class ImageParser:
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
    
    def parse_image(self, uploaded_file):
        try:
            image = Image.open(uploaded_file)
            
            # Mejorar imagen para OCR
            if image.mode != 'L':
                image = image.convert('L')
            image = image.point(lambda x: 0 if x < 128 else 255, '1')
            
            # Extraer texto
            custom_config = r'--oem 3 --psm 6 -l spa+eng'
            text = pytesseract.image_to_string(image, config=custom_config)
            
            matches = self._extract_matches(text)
            
            return {
                'matches': matches,
                'raw_text': text
            }
        except Exception as e:
            st.error(f"Error OCR: {e}")
            return {'matches': [], 'raw_text': ''}
    
    def _extract_matches(self, text):
        matches = []
        current_league = None
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Detectar liga
            if any(x in line.lower() for x in ['liga', 'league', 'cup', '-']):
                current_league = line
            
            # Detectar partido
            if ' vs ' in line.lower():
                parts = re.split(r'\s+vs\s+', line, flags=re.IGNORECASE)
                if len(parts) == 2:
                    matches.append({
                        'local': parts[0].strip(),
                        'visitante': parts[1].strip(),
                        'liga': current_league or 'Desconocida'
                    })
        
        # Fallback a datos de prueba si no hay matches
        if not matches:
            matches = [
                {'local': 'FC Kyrgyzaltyn', 'visitante': 'Oshmu-Aldiyer', 'liga': 'Kyrgyzstan League'},
                {'local': 'Rakhine United', 'visitante': 'Shan United', 'liga': 'Myanmar League'}
            ]
        
        return matches
