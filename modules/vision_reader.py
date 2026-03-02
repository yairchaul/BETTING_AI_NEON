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
    
    def is_odd(self, text: str) -> bool:
        """Detecta si un texto es una cuota"""
        cleaned = re.sub(r'\s+', '', text.strip())
        num_part = cleaned.replace('+', '').replace('-', '')
        try:
            val = float(num_part)
            # Cuotas americanas son >100, decimales entre 1 y 10
            return abs(val) >= 100 or (1 < val < 10)
        except:
            return False
    
    def is_team_name(self, text: str) -> bool:
        """Detecta si un texto es probable nombre de equipo"""
        if not text or len(text) < 3:
            return False
        
        # No debe ser un número
        if text.replace('.', '').replace('-', '').replace('+', '').isdigit():
            return False
        
        # No debe ser una fecha
        if re.match(r'\d{1,2}\s+[A-Za-z]{3}', text):
            return False
        
        # No debe ser una hora
        if re.match(r'\d{2}:\d{2}', text):
            return False
        
        # Palabras que no son equipos
        blacklist = ['empate', 'draw', 'vs', 'v', 'fc', 'cf', 'sc', 'ac', 'cd', 
                     'ud', 'sd', 'club', 'deportivo', 'real', 'united', 'city',
                     'athletic', 'sporting', 'racing', 'internacional']
        
        if text.lower() in blacklist:
            return False
        
        return True
    
    def clean_name(self, text: str) -> str:
        """Limpia el nombre del equipo"""
        # Quita códigos +XX al inicio
        text = re.sub(r'^\+\d+\s*', '', text)
        
        # Quita fechas al final (ej: "02 Mar 03:00")
        text = re.sub(r'\s*\d{1,2}\s+[A-Za-z]{3}\s*\d{2}:\d{2}$', '', text)
        
        # Quita códigos +XX en cualquier parte
        text = re.sub(r'\+\d+', '', text)
        
        # Quita caracteres especiales
        text = re.sub(r'[|•\-_=+*]', ' ', text)
        
        # Normaliza espacios
        text = ' '.join(text.split())
        
        return text.strip() if len(text) > 2 else ""
    
    def extract_words_with_coordinates(self, response):
        """Extrae palabras individuales con coordenadas"""
        word_list = []
        
        if not response.full_text_annotation or not response.full_text_annotation.pages:
            return word_list
        
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        word_text = ''.join(s.text for s in word.symbols).strip()
                        if not word_text:
                            continue
                        
                        # Calcular centro del
