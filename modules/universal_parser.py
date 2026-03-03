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
    
    def _preprocess_lines(self, lines):
        """Preprocesa líneas separando cuotas pegadas a 'Empate'"""
        processed_lines = []
        for line in lines:
            match = re.match(r'^([+-]\d{3,4})\s+(Empate.*?)$', line, re.IGNORECASE)
            if match:
                processed_lines.append(match.group(1))
                processed_lines.append(match.group(2))
            else:
                processed_lines.append(line)
        return processed_lines
    
    def parse(self, text):
        """Método principal: parsea texto plano"""
        raw_lines = [line.strip() for line in text.split('\n') if line.strip()]
        lines = self._preprocess_lines(raw_lines)
        
        matches = []
        
        # Estrategia 1: 6 líneas
        matches.extend(self._parse_six_line_format(lines))
        
        # Estrategia 2: 1 línea
        if len(matches) == 0:
            matches.extend(self._parse_one_line_format(lines))
        
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
            
            if 'empate' in empate_word.lower():
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
    
    def _parse_one_line_format(self, lines):
        """Formato: [Local] [Cuota L] [Empate] [Cuota E] [Visitante] [Cuota V]"""
        matches = []
        pattern = r'^(.+?)\s+([+-]\d{3,4})\s+([Ee]mpat[ea]?)\s+([+-]\d{3,4})\s+(.+?)\s+([+-]\d{3,4})$'
        for line in lines:
            match = re.match(pattern, line)
            if match:
                home_clean = re.sub(r'[|•\-_=+*]', '', match.group(1)).strip()
                away_clean = re.sub(r'[|•\-_=+*]', '', match.group(5)).strip()
                if (home_clean.lower() not in self.forbidden_words and 
                    away_clean.lower() not in self.forbidden_words):
                    matches.append({
                        'home': home_clean,
                        'away': away_clean,
                        'all_odds': [match.group(2), match.group(4), match.group(6)]
                    })
        return matches
