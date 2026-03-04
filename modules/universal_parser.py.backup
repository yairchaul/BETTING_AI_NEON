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
        # ESTRATEGIA 1: Formato de 10 LÍNEAS (el que acabas de mostrar)
        # ============================================================================
        ten_line_matches = self._parse_ten_line_format(lines)
        matches.extend(ten_line_matches)
        
        # ============================================================================
        # ESTRATEGIA 2: Formato de 6 COLUMNAS (una línea con 6 elementos)
        # ============================================================================
        if not matches:
            six_col_matches = self._parse_six_column_format(lines)
            matches.extend(six_col_matches)
        
        # ============================================================================
        # ESTRATEGIA 3: Formato de lista vertical
        # ============================================================================
        if not matches:
            vertical_matches = self._parse_vertical_list(lines)
            matches.extend(vertical_matches)
        
        # ============================================================================
        # ESTRATEGIA 4: Formato de 6 líneas
        # ============================================================================
        if not matches:
            six_line_matches = self._parse_six_line_format(lines)
            matches.extend(six_line_matches)
        
        # ============================================================================
        # ESTRATEGIA 5: Formato de 9 líneas
        # ============================================================================
        if not matches:
            nine_line_matches = self._parse_nine_line_format(lines)
            matches.extend(nine_line_matches)
        
        # Eliminar duplicados
        unique_matches = []
        seen = set()
        for match in matches:
            key = (match.get('home', ''), match.get('away', ''))
            if key not in seen:
                seen.add(key)
                unique_matches.append(match)
        
        return unique_matches
    
    def _parse_ten_line_format(self, lines):
        """
        Formato de 10 líneas por partido:
        1: +273 (código)
        2: Pumas UNAM (local)
        3: Toluca (visitante)
        4: 03 Mar 21:10 (fecha)
        5: 1
        6: ✗ (o X)
        7: 2
        8: +285 (cuota local)
        9: +280 (cuota empate)
        10: -118 (cuota visitante)
        """
        matches = []
        i = 0
        
        while i < len(lines) - 9:
            # Verificar que tenemos 10 líneas
            if i + 9 < len(lines):
                # Verificar que las líneas 5,6,7 son "1", "✗"/"X", "2"
                if (lines[i+4] in ['1', 'I'] and 
                    lines[i+5] in ['✗', 'X', 'x'] and 
                    lines[i+6] in ['2', 'II']):
                    
                    # Las líneas 8,9,10 son las cuotas
                    if (re.match(r'^[+-]\d+$', lines[i+7]) and
                        re.match(r'^[+-]\d+$', lines[i+8]) and
                        re.match(r'^[+-]\d+$', lines[i+9])):
                        
                        home = lines[i+1].strip()
                        away = lines[i+2].strip()
                        
                        # Limpiar nombres
                        home_clean = re.sub(r'[|•\-_=+*]', '', home).strip()
                        away_clean = re.sub(r'[|•\-_=+*]', '', away).strip()
                        
                        # Verificar que sean nombres válidos
                        if (len(home_clean) > 2 and len(away_clean) > 2 and
                            home_clean.lower() not in self.forbidden_words and
                            away_clean.lower() not in self.forbidden_words):
                            
                            matches.append({
                                'home': home_clean,
                                'away': away_clean,
                                'all_odds': [lines[i+7], lines[i+8], lines[i+9]],
                                'metadata': lines[i],  # +273
                                'fecha': lines[i+3]
                            })
                            
                            i += 10
                            continue
            i += 1
        
        return matches
    
    def _parse_six_column_format(self, lines):
        """
        Formato de 1 línea con 6 columnas:
        [Local] [Cuota L] [Empate] [Cuota E] [Visitante] [Cuota V]
        """
        matches = []
        pattern = r'^(.+?)\s+([+-]\d{3,4})\s+([Ee]mpat[ea]?)\s+([+-]\d{3,4})\s+(.+?)\s+([+-]\d{3,4})$'
        
        for line in lines:
            match = re.match(pattern, line)
            if match:
                home = match.group(1).strip()
                home_odd = match.group(2)
                empate_word = match.group(3)
                empate_odd = match.group(4)
                away = match.group(5).strip()
                away_odd = match.group(6)
                
                # Limpiar nombres
                home_clean = re.sub(r'[|•\-_=+*]', '', home).strip()
                away_clean = re.sub(r'[|•\-_=+*]', '', away).strip()
                
                # Verificar que sean nombres válidos
                if (len(home_clean) > 2 and len(away_clean) > 2 and
                    home_clean.lower() not in self.forbidden_words and
                    away_clean.lower() not in self.forbidden_words):
                    
                    matches.append({
                        'home': home_clean,
                        'away': away_clean,
                        'all_odds': [home_odd, empate_odd, away_odd]
                    })
        
        return matches
    
    def _parse_vertical_list(self, lines):
        """Parsea formato de lista vertical"""
        matches = []
        
        all_odds = []
        for line in lines:
            odds_in_line = re.findall(r'[+-]\d{3,4}', line)
            all_odds.extend(odds_in_line)
        
        team_names = []
        for line in lines:
            if not re.search(r'[+-]\d{3,4}', line) and re.search(r'[A-Za-z]', line):
                clean_name = re.sub(r'[|•\-_=+*]', '', line).strip()
                if len(clean_name) > 3 and clean_name.lower() not in self.forbidden_words:
                    team_names.append(clean_name)
        
        if len(team_names) >= 2:
            for i in range(0, len(team_names) - 1, 2):
                if i + 1 < len(team_names):
                    idx_odds = i
                    if idx_odds + 2 < len(all_odds):
                        matches.append({
                            'home': team_names[i],
                            'away': team_names[i + 1],
                            'all_odds': [
                                all_odds[idx_odds],
                                all_odds[idx_odds + 1],
                                all_odds[idx_odds + 2] if idx_odds + 2 < len(all_odds) else 'N/A'
                            ]
                        })
        
        return matches
    
    def _parse_six_line_format(self, lines):
        """Formato de 6 líneas por partido"""
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
                if (re.match(r'^[+-]\d+$', home_odd) and
                    re.match(r'^[+-]\d+$', empate_odd) and
                    re.match(r'^[+-]\d+$', away_odd)):
                    
                    home_clean = re.sub(r'[|•\-_=+*]', '', home).strip()
                    away_clean = re.sub(r'[|•\-_=+*]', '', away).strip()
                    
                    if (home_clean.lower() not in self.forbidden_words and 
                        away_clean.lower() not in self.forbidden_words):
                        
                        matches.append({
                            'home': home_clean,
                            'away': away_clean,
                            'all_odds': [home_odd, empate_odd, away_odd]
                        })
                        i += 6
                        continue
            i += 1
        return matches
    
    def _parse_nine_line_format(self, lines):
        """Formato de 9 líneas por partido"""
        matches = []
        i = 0
        while i < len(lines) - 8:
            if re.match(r'^[+-]\d+$', lines[i]):
                if lines[i+4] == '1' and lines[i+5] == '2':
                    matches.append({
                        'home': lines[i+1],
                        'away': lines[i+2],
                        'all_odds': [lines[i+6], lines[i+7], lines[i+8]]
                    })
                    i += 9
                    continue
            i += 1
        return matches