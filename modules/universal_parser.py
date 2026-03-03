# modules/universal_parser.py
import re
import streamlit as st

class UniversalParser:
    """
    Parser universal que detecta automáticamente el formato de la imagen
    y extrae los partidos correctamente.
    """
    
    def __init__(self):
        self.forbidden_words = ['empate', 'empaté', 'draw', 'vs', 'v', 'local', 'visitante', 'cuota', 'odds']
    
    def parse(self, text):
        """Método principal: detecta el formato y parsea"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # DEBUG: Mostrar líneas detectadas
        st.write("📄 Líneas detectadas por OCR:", lines)
        
        # ESTRATEGIA 1: Formato de 9 líneas (tu imagen actual)
        matches = self._parse_nine_line_format(lines)
        if matches:
            return matches
        
        # ESTRATEGIA 2: Formato flexible de 8-10 líneas
        matches = self._parse_flexible_format(lines)
        if matches:
            return matches
        
        # ESTRATEGIA 3: Formato de bloques humanos
        matches = self._parse_human_style(lines)
        if matches:
            return matches
        
        # ESTRATEGIA 4: Formato de 6 líneas
        matches = self._parse_six_line_format(lines)
        if matches:
            return matches
        
        # ESTRATEGIA 5: Formato de 1 línea (6 columnas)
        matches = self._parse_one_line_format(lines)
        if matches:
            return matches
        
        # ESTRATEGIA 6: Formato de 2 líneas
        matches = self._parse_two_line_format(lines)
        if matches:
            return matches
        
        return []
    
    def _parse_nine_line_format(self, lines):
        """
        Formato específico de 9 líneas:
        1: +XX (metadata)
        2: Equipo Local
        3: Equipo Visitante
        4: Fecha
        5: 1
        6: 2
        7: Cuota Local
        8: Cuota Empate
        9: Cuota Visitante
        """
        matches = []
        i = 0
        
        while i < len(lines):
            # Verificar si tenemos al menos 9 líneas para un bloque completo
            if i + 8 < len(lines):
                # Verificar si la línea actual es un número con signo
                if re.match(r'^[+-]\d+$', lines[i]):
                    local = lines[i+1]
                    visitante = lines[i+2]
                    fecha = lines[i+3]
                    
                    # Verificar las líneas 5 y 6 (deben ser "1" y "2")
                    if lines[i+4] == '1' and lines[i+5] == '2':
                        
                        # Las líneas 7, 8, 9 son las cuotas
                        cuota_local = lines[i+6]
                        cuota_empate = lines[i+7]
                        cuota_visitante = lines[i+8]
                        
                        # Validar que las cuotas tengan formato correcto
                        if (re.match(r'^[+-]\d+$', cuota_local) and
                            re.match(r'^[+-]\d+$', cuota_empate) and
                            re.match(r'^[+-]\d+$', cuota_visitante)):
                            
                            # Limpiar nombres (quitar (W), (R), etc.)
                            local_clean = re.sub(r'\s*\([^)]*\)', '', local).strip()
                            visitante_clean = re.sub(r'\s*\([^)]*\)', '', visitante).strip()
                            
                            matches.append({
                                'home': local_clean,
                                'away': visitante_clean,
                                'all_odds': [cuota_local, cuota_empate, cuota_visitante],
                                'fecha': fecha,
                                'metadata': lines[i]
                            })
                            
                            # Saltar las 9 líneas procesadas
                            i += 9
                            continue
            
            i += 1
        
        return matches
    
    def _parse_flexible_format(self, lines):
        """
        Formato flexible que acepta variaciones:
        +16
        Sheger Ketema (W)
        Mechal SC (W)
        03 Mar 01:00
        1
        [X] (opcional)
        2
        +200
        +180
        +130
        """
        matches = []
        i = 0
        
        while i < len(lines):
            if i + 7 < len(lines):
                if re.match(r'^[+-]\d+$', lines[i]):
                    potencial_local = lines[i+1]
                    potencial_visitante = lines[i+2]
                    potencial_fecha = lines[i+3]
                    
                    offset = 4
                    
                    # Verificar si la línea 4 es "1"
                    if i+offset < len(lines) and lines[i+offset] == '1':
                        offset += 1
                        
                        # Verificar si la siguiente línea es "X" (opcional)
                        if i+offset < len(lines) and lines[i+offset] == 'X':
                            offset += 1
                        
                        # Verificar si la siguiente línea es "2"
                        if i+offset < len(lines) and lines[i+offset] == '2':
                            offset += 1
                            
                            if i+offset+2 < len(lines):
                                cuota_local = lines[i+offset]
                                cuota_empate = lines[i+offset+1]
                                cuota_visitante = lines[i+offset+2]
                                
                                if (re.match(r'^[+-]\d+$', cuota_local) and
                                    re.match(r'^[+-]\d+$', cuota_visitante)):
                                    
                                    if not re.match(r'^[+-]\d+$', cuota_empate):
                                        cuota_empate = 'N/A'
                                    
                                    local_clean = re.sub(r'\s*\([^)]*\)', '', potencial_local).strip()
                                    visitante_clean = re.sub(r'\s*\([^)]*\)', '', potencial_visitante).strip()
                                    
                                    matches.append({
                                        'home': local_clean,
                                        'away': visitante_clean,
                                        'all_odds': [cuota_local, cuota_empate, cuota_visitante],
                                        'fecha': potencial_fecha
                                    })
                                    
                                    i += offset + 3
                                    continue
            
            i += 1
        
        return matches
    
    def _parse_human_style(self, lines):
        """Formato de bloques con estructura flexible"""
        matches = []
        i = 0
        
        while i < len(lines):
            if re.match(r'^[+-]\d+$', lines[i]):
                if i + 3 < len(lines):
                    local = lines[i+1]
                    visitante = lines[i+2]
                    fecha = lines[i+3]
                    
                    odds = []
                    j = i + 4
                    cuotas_encontradas = 0
                    
                    while j < len(lines) and cuotas_encontradas < 3:
                        linea = lines[j]
                        
                        match_1 = re.match(r'^(\d)\s+([+-]\d+)$', linea)
                        if match_1:
                            odds.append(match_1.group(2))
                            cuotas_encontradas += 1
                            j += 1
                            continue
                        
                        match_2 = re.match(r'^[+-]\d+$', linea)
                        if match_2:
                            odds.append(linea)
                            cuotas_encontradas += 1
                            j += 1
                            continue
                        
                        if linea in ['A', 'X']:
                            odds.append('N/A')
                            cuotas_encontradas += 1
                            j += 1
                            continue
                        
                        break
                    
                    if len(odds) >= 2:
                        while len(odds) < 3:
                            odds.append('N/A')
                        
                        local_clean = re.sub(r'\s*\([^)]*\)', '', local).strip()
                        visitante_clean = re.sub(r'\s*\([^)]*\)', '', visitante).strip()
                        
                        liga = "Desconocida"
                        if i > 0 and len(lines[i-1]) > 5:
                            liga = lines[i-1]
                        
                        matches.append({
                            'home': local_clean,
                            'away': visitante_clean,
                            'all_odds': odds[:3],
                            'liga': liga,
                            'fecha': fecha
                        })
                        
                        i = j
                        continue
            
            i += 1
        
        return matches
    
    def _parse_six_line_format(self, lines):
        """Formato C: 6 líneas por partido"""
        matches = []
        i = 0
        while i < len(lines) - 5:
            home = lines[i]
            home_odd = lines[i+1]
            empate_word = lines[i+2]
            empate_odd = lines[i+3]
            away = lines[i+4]
            away_odd = lines[i+5]
            
            if ('empate' in empate_word.lower()):
                if (re.match(r'^[+-]\d{3,4}$', home_odd) and
                    re.match(r'^[+-]\d{3,4}$', empate_odd) and
                    re.match(r'^[+-]\d{3,4}$', away_odd)):
                    
                    if self._is_valid_team(home) and self._is_valid_team(away):
                        matches.append({
                            'home': home,
                            'away': away,
                            'all_odds': [home_odd, empate_odd, away_odd]
                        })
                        i += 6
                        continue
            i += 1
        return matches
    
    def _parse_one_line_format(self, lines):
        """Formato A: 1 línea con 6 elementos"""
        matches = []
        pattern = r'^(.+?)\s+([+-]\d{3,4})\s+([Ee]mpat[ea]?[i]?[e]?)\s+([+-]\d{3,4})\s+(.+?)\s+([+-]\d{3,4})$'
        
        for line in lines:
            match = re.match(pattern, line)
            if match:
                home = match.group(1).strip()
                local_odd = match.group(2)
                empate_odd = match.group(4)
                away = match.group(5).strip()
                away_odd = match.group(6)
                
                if self._is_valid_team(home) and self._is_valid_team(away):
                    matches.append({
                        'home': home,
                        'away': away,
                        'all_odds': [local_odd, empate_odd, away_odd]
                    })
        return matches
    
    def _parse_two_line_format(self, lines):
        """Formato B: 2 líneas por partido"""
        matches = []
        i = 0
        while i < len(lines) - 1:
            line1 = lines[i]
            line2 = lines[i+1]
            
            odds_line1 = re.findall(r'[+-]\d{3,4}', line1)
            
            if len(odds_line1) >= 2 and not re.search(r'[+-]\d{3,4}', line2):
                local_part = line1.split(odds_line1[0])[0].strip()
                home = re.sub(r'Empate.*', '', local_part).strip()
                away = line2.strip()
                
                if self._is_valid_team(home) and self._is_valid_team(away):
                    away_odd = odds_line1[2] if len(odds_line1) > 2 else 'N/A'
                    matches.append({
                        'home': home,
                        'away': away,
                        'all_odds': [odds_line1[0], odds_line1[1], away_odd]
                    })
                i += 2
            else:
                i += 1
        return matches
    
    def _is_valid_team(self, name):
        """Valida que un nombre sea un equipo válido"""
        if not name or len(name) < 2:
            return False
        if name.lower() in self.forbidden_words:
            return False
        if re.match(r'^[+-]?\d+$', name):
            return False
        return True