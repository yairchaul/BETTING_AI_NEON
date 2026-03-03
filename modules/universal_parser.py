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
        """
        Método principal: detecta el formato y parsea
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # DEBUG: Mostrar líneas detectadas (solo si es necesario)
        # st.write("Líneas detectadas:", lines)
        
        # Intentar cada formato en orden de probabilidad
        parsers = [
            self._parse_format_c,  # 6 líneas (más común en capturas)
            self._parse_format_d,  # Bloques complejos (como tu imagen)
            self._parse_format_a,  # 1 línea con 6 columnas
            self._parse_format_b,  # 2 líneas
        ]
        
        for parser in parsers:
            matches = parser(lines)
            if matches:
                return matches
        
        return []
    
    def _parse_format_a(self, lines):
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
    
    def _parse_format_b(self, lines):
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
    
    def _parse_format_c(self, lines):
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
    
    def _parse_format_d(self, lines):
        """Formato D: Bloques complejos (como tu imagen)"""
        matches = []
        i = 0
        while i < len(lines):
            # Saltar números sueltos al inicio (como +90, +16, etc.)
            if re.match(r'^[+-]\d+$', lines[i]) and i + 5 < len(lines):
                i += 1
                continue
            
            # Buscar patrón de bloque
            if i + 4 < len(lines):
                # Posible liga (puede tener números)
                liga = lines[i]
                
                # Buscar dos líneas que parezcan equipos
                if i+2 < len(lines):
                    home_candidate = lines[i]
                    away_candidate = lines[i+1]
                    fecha_candidate = lines[i+2]
                    
                    # Buscar cuotas en las siguientes líneas
                    odds = []
                    j = i+3
                    while j < len(lines) and len(odds) < 3:
                        # Buscar patrón "1 +XXX" o "+XXX" suelto
                        match = re.match(r'^(\d)\s+([+-]\d+)$', lines[j])
                        if match:
                            odds.append(match.group(2))
                        elif re.match(r'^[+-]\d+$', lines[j]) and len(odds) < 3:
                            odds.append(lines[j])
                        j += 1
                    
                    if len(odds) >= 2:  # Al menos 2 odds (puede faltar una)
                        # Limpiar nombres
                        home_clean = re.sub(r'\s*\([^)]*\)', '', home_candidate).strip()
                        away_clean = re.sub(r'\s*\([^)]*\)', '', away_candidate).strip()
                        
                        if self._is_valid_team(home_clean) and self._is_valid_team(away_clean):
                            # Completar odds si faltan
                            while len(odds) < 3:
                                odds.append('N/A')
                            
                            matches.append({
                                'home': home_clean,
                                'away': away_clean,
                                'all_odds': odds[:3],
                                'liga': liga,
                                'fecha': fecha_candidate
                            })
                        i = j
                        continue
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