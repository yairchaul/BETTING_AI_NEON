# modules/universal_parser.py
import re
import streamlit as st

class UniversalParser:
    """
    Parser universal que detecta automáticamente TODOS los formatos de imagen
    y extrae los partidos correctamente.
    """

    def __init__(self):
        self.forbidden_words = ['empate', 'empaté', 'draw', 'vs', 'v', 'local', 'visitante', 'cuota', 'odds']

    def parse(self, text):
        """Método principal: detecta TODOS los formatos y parsea"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # DEBUG: Mostrar líneas detectadas
        st.write("📄 Líneas detectadas por OCR:", lines)

        matches = []

        # ============================================================================
        # ESTRATEGIA 1: Formato ESPECÍFICO de Caliente.mx (el que acabas de mostrar)
        # ============================================================================
        formato_caliente = self._parse_caliente_format(lines)
        matches.extend(formato_caliente)

        # ============================================================================
        # ESTRATEGIA 2: Formato de 10 LÍNEAS
        # ============================================================================
        if not matches:
            ten_line_matches = self._parse_ten_line_format(lines)
            matches.extend(ten_line_matches)

        # ============================================================================
        # ESTRATEGIA 3: Formato de 6 COLUMNAS (una línea con 6 elementos)
        # ============================================================================
        if not matches:
            six_col_matches = self._parse_six_column_format(lines)
            matches.extend(six_col_matches)

        # ============================================================================
        # ESTRATEGIA 4: Formato de lista vertical
        # ============================================================================
        if not matches:
            vertical_matches = self._parse_vertical_list(lines)
            matches.extend(vertical_matches)

        # ============================================================================
        # ESTRATEGIA 5: Formato de 6 líneas
        # ============================================================================
        if not matches:
            six_line_matches = self._parse_six_line_format(lines)
            matches.extend(six_line_matches)

        return matches

    def _parse_caliente_format(self, lines):
        """
        Formato específico de Caliente.mx:
        [Local, "cuota_local Empate", cuota_empate, Visitante, cuota_visitante]
        Ejemplo: ["Puebla", "+270 Empate", "+255", "Tigres UANL", "-103"]
        """
        matches = []
        i = 0
        
        while i < len(lines):
            try:
                # Buscar patrón: nombre del equipo local
                local = lines[i]
                if any(word in local.lower() for word in ['empate', 'draw', 'vs']):
                    i += 1
                    continue
                
                # Línea de cuota local (puede tener "Empate" al final)
                cuota_local_line = lines[i+1]
                
                # Extraer la cuota local (números con + o -)
                match = re.search(r'([+-]?\d+)', cuota_local_line)
                if not match:
                    i += 1
                    continue
                cuota_local = match.group(1)
                
                # Cuota de empate
                cuota_empate = lines[i+2]
                if not re.match(r'[+-]?\d+', cuota_empate):
                    i += 1
                    continue
                
                # Visitante
                visitante = lines[i+3]
                if any(word in visitante.lower() for word in ['empate', 'draw']):
                    i += 1
                    continue
                
                # Cuota visitante
                cuota_visitante = lines[i+4]
                if not re.match(r'[+-]?\d+', cuota_visitante):
                    i += 1
                    continue
                
                # Si llegamos aquí, tenemos un partido válido
                partido = {
                    'local': local,
                    'cuota_local': cuota_local,
                    'empate': 'Empate',
                    'cuota_empate': cuota_empate,
                    'visitante': visitante,
                    'cuota_visitante': cuota_visitante
                }
                matches.append(partido)
                
                # Avanzar 5 líneas para el siguiente partido
                i += 5
                
            except IndexError:
                break
            except Exception:
                i += 1
                
        return matches

    def _parse_ten_line_format(self, lines):
        """Formato donde cada partido ocupa 10 líneas"""
        matches = []
        i = 0
        while i + 9 < len(lines):
            try:
                local = lines[i]
                cuota_local = lines[i+1]
                empate = lines[i+2]
                cuota_empate = lines[i+3]
                visitante = lines[i+4]
                cuota_visitante = lines[i+5]
                
                # Verificar que tenga sentido
                if re.match(r'[+-]?\d+', cuota_local) and re.match(r'[+-]?\d+', cuota_visitante):
                    partido = {
                        'local': local,
                        'cuota_local': cuota_local,
                        'empate': empate,
                        'cuota_empate': cuota_empate,
                        'visitante': visitante,
                        'cuota_visitante': cuota_visitante
                    }
                    matches.append(partido)
                i += 10
            except:
                i += 1
        return matches

    def _parse_six_column_format(self, lines):
        """Formato donde una línea contiene las 6 columnas"""
        matches = []
        pattern = re.compile(
            r'([A-Za-záéíóúñ\s]+?)\s+([+-]?\d+)\s+(empate|draw|emp)\s+([+-]?\d+)\s+([A-Za-záéíóúñ\s]+?)\s+([+-]?\d+)',
            re.IGNORECASE
        )
        
        for line in lines:
            match = pattern.search(line)
            if match:
                partido = {
                    'local': match.group(1).strip(),
                    'cuota_local': match.group(2),
                    'empate': 'Empate',
                    'cuota_empate': match.group(4),
                    'visitante': match.group(5).strip(),
                    'cuota_visitante': match.group(6)
                }
                matches.append(partido)
        return matches

    def _parse_vertical_list(self, lines):
        """Formato donde los equipos aparecen en una lista vertical"""
        matches = []
        i = 0
        while i + 5 < len(lines):
            try:
                local = lines[i]
                cuota_local = lines[i+1]
                empate = lines[i+2]
                cuota_empate = lines[i+3]
                visitante = lines[i+4]
                cuota_visitante = lines[i+5]
                
                # Verificar que las cuotas son números
                if (re.match(r'[+-]?\d+', cuota_local) and 
                    re.match(r'[+-]?\d+', cuota_empate) and 
                    re.match(r'[+-]?\d+', cuota_visitante)):
                    
                    partido = {
                        'local': local,
                        'cuota_local': cuota_local,
                        'empate': empate,
                        'cuota_empate': cuota_empate,
                        'visitante': visitante,
                        'cuota_visitante': cuota_visitante
                    }
                    matches.append(partido)
                i += 6
            except:
                i += 1
        return matches

    def _parse_six_line_format(self, lines):
        """Formato genérico de 6 líneas"""
        return self._parse_vertical_list(lines)
