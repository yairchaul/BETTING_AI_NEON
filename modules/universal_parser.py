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
        
        # DEBUG: Mostrar líneas para verificar
        # st.write("📄 Líneas:", lines)
        
        matches = []
        
        # ESTRATEGIA 1: Formato de 5-6 líneas (el de tu imagen)
        matches = self._parse_five_six_line_format(lines)
        if matches:
            return matches
        
        # ESTRATEGIA 2: Formato de lista vertical
        matches = self._parse_vertical_list(lines)
        if matches:
            return matches
        
        # ESTRATEGIA 3: Formato de 1 línea (6 columnas)
        matches = self._parse_one_line_format(lines)
        if matches:
            return matches
        
        return []
    
    def _parse_five_six_line_format(self, lines):
        """
        Formato de 5-6 líneas por partido:
        Línea 1: Equipo Local
        Línea 2: Cuota Local + posible "Empate"
        Línea 3: Cuota Empate
        Línea 4: Equipo Visitante
        Línea 5: Cuota Visitante
        (Línea 6: puede ser el siguiente equipo o espacio)
        """
        matches = []
        i = 0
        
        while i < len(lines) - 4:
            # Tomar las primeras 5 líneas como posible partido
            line1 = lines[i]      # Equipo Local
            line2 = lines[i+1]    # Cuota Local + posible "Empate"
            line3 = lines[i+2]    # Cuota Empate
            line4 = lines[i+3]    # Equipo Visitante
            line5 = lines[i+4]    # Cuota Visitante
            
            # Extraer cuota local de line2
            local_odds = re.findall(r'[+-]\d{3,4}', line2)
            if not local_odds:
                i += 1
                continue
            
            local_odd = local_odds[0]
            
            # Validar que line3 y line5 sean cuotas
            if (re.match(r'^[+-]\d{3,4}$', line3) and
                re.match(r'^[+-]\d{3,4}$', line5)):
                
                # Limpiar nombres
                home = re.sub(r'[|•\-_=+*]', '', line1).strip()
                away = re.sub(r'[|•\-_=+*]', '', line4).strip()
                
                # Verificar que sean nombres válidos
                if (len(home) > 2 and len(away) > 2):
                    matches.append({
                        'home': home,
                        'away': away,
                        'all_odds': [local_odd, line3, line5]
                    })
                    
                    i += 5  # Saltar las 5 líneas procesadas
                    continue
            
            i += 1
        
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
    
    def _parse_one_line_format(self, lines):
        """Formato: [Local] [Cuota L] [Empate] [Cuota E] [Visitante] [Cuota V]"""
        matches = []
        pattern = r'^(.+?)\s+([+-]\d{3,4})\s+([Ee]mpat[ea]?)\s+([+-]\d{3,4})\s+(.+?)\s+([+-]\d{3,4})$'
        
        for line in lines:
            match = re.match(pattern, line)
            if match:
                matches.append({
                    'home': match.group(1).strip(),
                    'away': match.group(5).strip(),
                    'all_odds': [match.group(2), match.group(4), match.group(6)]
                })
        return matches
