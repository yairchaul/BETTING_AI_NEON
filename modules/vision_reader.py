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
        """Procesa la imagen y extrae pares de equipos con múltiples estrategias"""
        if not self.client:
            return []
        
        try:
            image = vision.Image(content=image_bytes)
            response = self.client.document_text_detection(image=image)
            texts = response.text_annotations

            if not texts:
                return []

            full_text = texts[0].description
            
            # ============================================================================
            # VALIDADOR: Mostrar texto completo para depuración
            # ============================================================================
            st.info("📄 **Texto completo detectado por OCR:**")
            st.code(full_text)
            
            # Intentar múltiples estrategias de parsing
            matches = []
            
            # ESTRATEGIA 1: Patrón de 6 elementos en líneas separadas
            matches = self.parse_six_line_pattern(full_text)
            
            # ESTRATEGIA 2: Patrón de línea completa
            if not matches:
                matches = self.parse_single_line_pattern(full_text)
            
            # ESTRATEGIA 3: Patrón de tabla con separadores
            if not matches:
                matches = self.parse_table_pattern(full_text)
            
            # ESTRATEGIA 4: Extracción manual (último recurso)
            if not matches:
                matches = self.parse_manual_extraction(full_text)
            
            return matches
            
        except Exception as e:
            st.error(f"Error procesando imagen: {e}")
            return []

    def parse_six_line_pattern(self, text):
        """
        ESTRATEGIA 1: Busca el patrón de 6 líneas consecutivas:
        Línea 1: Equipo Local
        Línea 2: Cuota Local (+/-)
        Línea 3: "Empate"
        Línea 4: Cuota Empate
        Línea 5: Equipo Visitante
        Línea 6: Cuota Visitante
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        matches = []
        
        i = 0
        while i < len(lines) - 5:
            # Verificar las 6 líneas
            posibles = lines[i:i+6]
            
            # Validar cada línea
            if (self.is_team_name(posibles[0]) and
                self.is_odds(posibles[1]) and
                posibles[2] == "Empate" and
                self.is_odds(posibles[3]) and
                self.is_team_name(posibles[4]) and
                self.is_odds(posibles[5])):
                
                matches.append({
                    "home": posibles[0],
                    "away": posibles[4],
                    "all_odds": [posibles[1], posibles[3], posibles[5]]
                })
                i += 6
            else:
                i += 1
        
        return matches

    def parse_single_line_pattern(self, text):
        """
        ESTRATEGIA 2: Busca patrones en una sola línea
        Formato: "Real Madrid -278 Empate +340 Getafe +900"
        """
        lines = text.split('\n')
        matches = []
        
        # Patrón mejorado
        pattern = r'([A-Za-z\s]+?)\s+([+-]\d{3,4})\s+Empate\s+([+-]\d{3,4})\s+([A-Za-z\s]+?)\s+([+-]\d{3,4})'
        
        for line in lines:
            encontrado = re.search(pattern, line)
            if encontrado:
                matches.append({
                    "home": encontrado.group(1).strip(),
                    "away": encontrado.group(4).strip(),
                    "all_odds": [
                        encontrado.group(2),
                        encontrado.group(3),
                        encontrado.group(5)
                    ]
                })
        
        return matches

    def parse_table_pattern(self, text):
        """
        ESTRATEGIA 3: Interpreta como tabla de 2 columnas
        Primero todos los locales, luego todos los visitantes
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Separar en dos grupos: antes y después de los números
        equipos_locales = []
        cuotas_locales = []
        cuotas_empate = []
        equipos_visitantes = []
        cuotas_visitantes = []
        
        i = 0
        # Buscar los primeros 5 equipos (locales)
        while i < len(lines) and len(equipos_locales) < 5:
            if self.is_team_name(lines[i]) and "Empate" not in lines[i]:
                equipos_locales.append(lines[i])
                i += 1
                if i < len(lines) and self.is_odds(lines[i]):
                    cuotas_locales.append(lines[i])
                    i += 1
                    if i < len(lines) and lines[i] == "Empate":
                        i += 1
                        if i < len(lines) and self.is_odds(lines[i]):
                            cuotas_empate.append(lines[i])
                            i += 1
            else:
                i += 1
        
        # Buscar los 5 equipos visitantes
        while i < len(lines) and len(equipos_visitantes) < 5:
            if self.is_team_name(lines[i]) and "Empate" not in lines[i]:
                equipos_visitantes.append(lines[i])
                i += 1
                if i < len(lines) and self.is_odds(lines[i]):
                    cuotas_visitantes.append(lines[i])
                    i += 1
            else:
                i += 1
        
        # Construir matches
        matches = []
        for j in range(min(len(equipos_locales), len(equipos_visitantes))):
            if (j < len(cuotas_locales) and 
                j < len(cuotas_empate) and 
                j < len(cuotas_visitantes)):
                matches.append({
                    "home": equipos_locales[j],
                    "away": equipos_visitantes[j],
                    "all_odds": [
                        cuotas_locales[j],
                        cuotas_empate[j],
                        cuotas_visitantes[j]
                    ]
                })
        
        return matches

    def parse_manual_extraction(self, text):
        """
        ESTRATEGIA 4: Extracción manual basada en posiciones conocidas
        Para cuando las otras estrategias fallan
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Lista de equipos conocidos en LaLiga
        equipos_conocidos = [
            "Real Madrid", "Barcelona", "Atletico Madrid", "Sevilla", 
            "Real Betis", "Real Sociedad", "Athletic Bilbao", "Valencia",
            "Villarreal", "Osasuna", "Celta de Vigo", "Rayo Vallecano",
            "Getafe", "RCD Mallorca", "Girona", "Almeria",
            "Real Valladolid", "Espanyol", "Cadiz", "Elche",
            "Real Oviedo", "Levante", "Granada", "Las Palmas"
        ]
        
        # Extraer todos los equipos detectados
        equipos_detectados = []
        for line in lines:
            for equipo in equipos_conocidos:
                if equipo in line and line not in equipos_detectados:
                    equipos_detectados.append(line)
                    break
        
        # Extraer todas las odds
        odds_detectadas = [line for line in lines if self.is_odds(line)]
        
        # Si tenemos suficientes datos, construir matches manualmente
        matches = []
        if len(equipos_detectados) >= 10 and len(odds_detectadas) >= 15:
            locales = equipos_detectados[:5]
            visitantes = equipos_detectados[5:10]
            
            for j in range(5):
                idx_odds = j * 3
                if idx_odds + 2 < len(odds_detectadas):
                    matches.append({
                        "home": locales[j],
                        "away": visitantes[j],
                        "all_odds": [
                            odds_detectadas[idx_odds],
                            odds_detectadas[idx_odds + 1],
                            odds_detectadas[idx_odds + 2]
                        ]
                    })
        
        return matches

    def is_team_name(self, text):
        """Determina si un texto es probable nombre de equipo"""
        if not text or len(text) < 2:
            return False
        
        # No debe ser una odds
        if re.match(r'^[+-]\d{3,4}$', text):
            return False
        
        # No debe ser "Empate"
        if text == "Empate":
            return False
        
        # Debe contener letras
        if not re.search(r'[A-Za-z]', text):
            return False
        
        # No debe ser una fecha u hora
        if re.match(r'\d{1,2}\s+[A-Za-z]{3}', text) or re.match(r'\d{2}:\d{2}', text):
            return False
        
        return True

    def is_odds(self, text):
        """Determina si un texto es una odds"""
        return bool(re.match(r'^[+-]\d{3,4}$', text))

    def clean_team_name(self, name):
        """Limpia el nombre del equipo"""
        name = re.sub(r'[0-9+\-]', '', name)
        name = re.sub(r'\s+', ' ', name).strip()
        return name


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
