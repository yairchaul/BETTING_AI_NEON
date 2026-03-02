# modules/ocr_reader.py
import re
import streamlit as st
from google.cloud import vision

class ImageParser:
    def __init__(self):
        """Inicializa el cliente de Google Vision usando secrets"""
        try:
            credentials = dict(st.secrets["google_credentials"])
            self.client = vision.ImageAnnotatorClient.from_service_account_info(credentials)
        except Exception as e:
            st.error(f"Error inicializando Google Vision: {e}")
            self.client = None
    
    def clean_ocr_noise(self, text):
        """Elimina ruidos de la interfaz y nombres de ligas."""
        # Eliminar fechas, horas y marcadores
        text = re.sub(r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\d{2}:\d{2}', '', text)
        text = re.sub(r'\+\s*\d+', '', text)
        text = re.sub(r'[|•\-_]', ' ', text)
        
        # Lista negra ampliada
        blacklist = [
            "Europa", "Rumania", "Turquía", "Italia", "Liga 2", "Liga 3", 
            "TFF League", "Primavera", "Championship", "Resultado", "Final", 
            "1", "X", "2", "Directo", "Hoy", "Mañana", "Puntos", "Score",
            "Points", "Asia", "Australia", "Europa", "Fútbol", "Mujeres",
            "Women", "International", "Euro", "Qualifiers", "Sub-19", "U19",
            "State League", "Premier League", "National League", "Pervaya Liga",
            "Victoria", "Eltham", "Bulleen", "Kyrgyzstan", "Myanmar", "Rakhine",
            "Shan United", "FC Kyrgyzaltyn", "Oshmu-Aldiyer"  # Eliminamos ejemplos
        ]
        for word in blacklist:
            text = text.replace(word, "")
        
        return text.strip()
    
    def normalize_team_name(self, name):
        """Normaliza nombres de equipos para mejor matching"""
        # Eliminar números y caracteres especiales
        name = re.sub(r'[0-9+\-]', '', name)
        # Eliminar palabras comunes
        common = ['FC', 'CF', 'SC', 'AC', 'CD', 'UD', 'SD', 'Club', 'Deportivo']
        for word in common:
            name = name.replace(word, '')
        # Limpiar espacios
        name = ' '.join(name.split())
        return name.strip()
    
    def extract_odds_from_line(self, line):
        """Extrae cuotas de una línea de texto"""
        # Patrón para momios americanos (+/- seguido de 3-4 dígitos)
        odds_pattern = r'[+-]\d{3,4}'
        return re.findall(odds_pattern, line)
    
    def parse_image(self, uploaded_file):
        """Procesa la imagen con Google Vision y extrae los partidos"""
        
        if not self.client:
            st.error("Google Vision no inicializado")
            return {'matches': [], 'raw_text': '', 'odds_detected': []}
        
        try:
            content = uploaded_file.getvalue()
            image = vision.Image(content=content)
            response = self.client.text_detection(image=image)
            
            if not response.text_annotations:
                return {'matches': [], 'raw_text': '', 'odds_detected': []}
            
            full_text = response.text_annotations[0].description
            
            # Extraer TODOS los momios americanos
            all_odds = re.findall(r'[+-]\d{3,4}', full_text)
            
            # Limpiar texto
            clean_text = self.clean_ocr_noise(full_text)
            
            # Dividir en líneas y filtrar
            lines = [l.strip() for l in clean_text.split('\n') if len(l.strip()) > 2]
            
            matches = []
            
            # ESTRATEGIA 1: Buscar patrones de 2 líneas consecutivas con odds
            i = 0
            while i < len(lines) - 1:
                line1 = lines[i]
                line2 = lines[i + 1]
                
                # Verificar si hay odds disponibles
                if len(all_odds) >= 3:
                    # Tomar las primeras 3 odds
                    odds = all_odds[:3]
                    all_odds = all_odds[3:]
                    
                    # Limpiar nombres
                    home = self.normalize_team_name(line1)
                    away = self.normalize_team_name(line2)
                    
                    # Validar que sean nombres válidos
                    if (len(home) > 2 and len(away) > 2 and 
                        not home.isdigit() and not away.isdigit() and
                        not any(x in home.lower() for x in ['score', 'points', 'total'])):
                        
                        matches.append({
                            "home": home,
                            "away": away,
                            "odds": odds,
                            "liga": "Detectada de imagen"
                        })
                        i += 2  # Saltar ambas líneas
                        continue
                i += 1
            
            # ESTRATEGIA 2: Si no funcionó, buscar en una sola línea
            if not matches:
                for line in lines:
                    odds_in_line = self.extract_odds_from_line(line)
                    if len(odds_in_line) >= 3:
                        # Separar equipo local y visitante (antes y después de las odds)
                        parts = re.split(r'[+-]\d{3,4}', line)
                        if len(parts) >= 2:
                            home = self.normalize_team_name(parts[0])
                            away = self.normalize_team_name(parts[-1])
                            
                            if home and away and len(home) > 2 and len(away) > 2:
                                matches.append({
                                    "home": home,
                                    "away": away,
                                    "odds": odds_in_line[:3],
                                    "liga": "Detectada de imagen"
                                })
            
            # IMPORTANTE: NO HAY FALLBACK - si no hay matches, lista vacía
            return {
                'matches': matches,
                'raw_text': full_text,
                'odds_detected': re.findall(r'[+-]\d{3,4}', full_text)
            }
            
        except Exception as e:
            st.error(f"Error en OCR: {e}")
            return {'matches': [], 'raw_text': '', 'odds_detected': []}
