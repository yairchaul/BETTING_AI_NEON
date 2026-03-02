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
        """Lógica mejorada para extraer equipos ignorando 'Empate' y otros ruidos"""
        lines = text.split('\n')
        matches = []
        
        # 1. Extraer todas las odds primero
        all_odds = re.findall(r'[+-]\d{3,4}', text)
        
        # 2. Limpiar líneas y preparar para procesamiento
        clean_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Ignorar líneas que son solo odds
            if re.match(r'^[+-]?\d+[.,]?\d*$', line):
                continue
            # Ignorar horas y fechas
            if re.match(r'^\d{2}:\d{2}$', line):
                continue
            if re.match(r'^\d{1,2}\s+[A-Za-z]{3}', line):
                continue
            
            # Limpiar caracteres especiales
            line = re.sub(r'[|•\-_=+*]', ' ', line)
            line = re.sub(r'\s+', ' ', line).strip()
            
            if len(line) > 2:
                clean_lines.append(line)
        
        # 3. Procesar las líneas para encontrar el patrón: EQUIPO - ODDS - EQUIPO
        i = 0
        odds_index = 0
        
        while i < len(clean_lines) and odds_index + 2 < len(all_odds):
            current_line = clean_lines[i]
            
            # Buscar si la línea actual parece un equipo (no contiene "Empate")
            if self.is_team_name(current_line) and "empate" not in current_line.lower():
                home = current_line
                
                # Las siguientes 3 odds son para este partido
                odds = all_odds[odds_index:odds_index + 3]
                odds_index += 3
                
                # Buscar el equipo visitante en las siguientes líneas
                j = i + 1
                away_found = None
                
                while j < len(clean_lines):
                    next_line = clean_lines[j]
                    # El visitante debe ser un nombre de equipo y no contener "Empate"
                    if self.is_team_name(next_line) and "empate" not in next_line.lower():
                        away_found = next_line
                        break
                    j += 1
                
                if away_found:
                    matches.append({
                        "home": self.fix_common_names(home),
                        "away": self.fix_common_names(away_found),
                        "all_odds": odds
                    })
                    i = j + 1  # Saltar hasta después del visitante
                    continue
            i += 1
        
        # 4. Si no encontró con el método anterior, intentar con patrón alternativo
        if not matches:
            # Buscar líneas que contengan odds y dos equipos
            for line in clean_lines:
                odds_in_line = re.findall(r'[+-]\d{3,4}', line)
                if len(odds_in_line) >= 3:
                    # Separar por espacios
                    parts = line.split()
                    # Filtrar partes que no sean odds y no sean "Empate"
                    team_parts = [p for p in parts if not re.match(r'[+-]\d+', p) and p.lower() != "empate"]
                    
                    if len(team_parts) >= 2:
                        matches.append({
                            "home": self.fix_common_names(team_parts[0]),
                            "away": self.fix_common_names(team_parts[-1]),
                            "all_odds": odds_in_line[:3]
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
            "Real": "Real Madrid",  # Esto debería ser más específico en producción
            "Atleti": "Atletico Madrid",
            "Barca": "Barcelona",
            "PSG": "Paris Saint Germain",
            "M'gladbach": "Borussia Monchengladbach",
            "U. Berlin": "Union Berlin",
            "Le Havre AC": "Le Havre"
        }
        
        # Solo aplicar corrección si el nombre exacto está en el diccionario
        return corrections.get(name, name)

    def is_valid_team_pair(self, t1, t2):
        """Valida que ambos sean nombres de equipo válidos"""
        return (self.is_team_name(t1) and 
                self.is_team_name(t2) and 
                "empate" not in t1.lower() and 
                "empate" not in t2.lower())


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
