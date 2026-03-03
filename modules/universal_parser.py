# modules/universal_parser.py
import re
import streamlit as st

class UniversalParser:
    """
    Parser universal que imita el razonamiento humano para detectar
    partidos en cualquier formato de imagen.
    """
    
    def __init__(self):
        self.forbidden_words = ['empate', 'empaté', 'draw', 'vs', 'v', 'local', 'visitante', 'cuota', 'odds']
    
    def parse(self, text):
        """Método principal: imita el proceso mental humano"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Un humano primero intentaría ver si hay bloques con números especiales
        matches = self._parse_human_style(lines)
        if matches:
            return matches
        
        # Si no, prueba los formatos estándar
        parsers = [
            self._parse_format_c,  # 6 líneas
            self._parse_format_a,  # 1 línea con 6 columnas
            self._parse_format_b,  # 2 líneas
        ]
        
        for parser in parsers:
            matches = parser(lines)
            if matches:
                return matches
        
        return []
    
    def _parse_human_style(self, lines):
        """
        Imita exactamente cómo un humano analizaría la imagen:
        - Busca bloques que empiezan con un número con signo (+90, +14, etc.)
        - Cada bloque tiene estructura fija
        """
        matches = []
        i = 0
        
        while i < len(lines):
            # Un humano detecta un nuevo bloque cuando ve un número con signo
            if re.match(r'^[+-]\d+$', lines[i]):
                
                # Verificar que hay suficientes líneas para un bloque completo
                if i + 3 < len(lines):
                    codigo = lines[i]      # Metadata (lo ignoramos)
                    local = lines[i+1]
                    visitante = lines[i+2]
                    fecha = lines[i+3]
                    
                    # Un humano sabe que después de la fecha vienen las cuotas
                    odds = []
                    j = i + 4
                    
                    # Buscar las próximas 3 líneas que sean cuotas
                    cuotas_encontradas = 0
                    while j < len(lines) and cuotas_encontradas < 3:
                        linea = lines[j]
                        
                        # Patrón "1 +125"
                        match_1 = re.match(r'^(\d)\s+([+-]\d+)$', linea)
                        if match_1:
                            odds.append(match_1.group(2))
                            cuotas_encontradas += 1
                            j += 1
                            continue
                        
                        # Patrón "+125" suelto
                        match_2 = re.match(r'^[+-]\d+$', linea)
                        if match_2 and cuotas_encontradas < 3:
                            odds.append(linea)
                            cuotas_encontradas += 1
                            j += 1
                            continue
                        
                        # Caso especial: "A" (sin cuota)
                        if linea == 'A' and cuotas_encontradas < 3:
                            odds.append('N/A')
                            cuotas_encontradas += 1
                            j += 1
                            continue
                        
                        # Si no es una cuota, dejamos de buscar
                        break
                    
                    # Si encontramos al menos 2 cuotas, es un bloque válido
                    if len(odds) >= 2:
                        # Completar con N/A si faltan
                        while len(odds) < 3:
                            odds.append('N/A')
                        
                        # Limpiar nombres (quitar (W), (R), etc.)
                        local_clean = re.sub(r'\s*\([^)]*\)', '', local).strip()
                        visitante_clean = re.sub(r'\s*\([^)]*\)', '', visitante).strip()
                        
                        # Inferir liga del contexto (línea anterior al bloque)
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
                        
                        # Saltar al siguiente bloque
                        i = j
                        continue
            
            i += 1
        
        return matches
    
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
    
    def _is_valid_team(self, name):
        """Valida que un nombre sea un equipo válido"""
        if not name or len(name) < 2:
            return False
        if name.lower() in self.forbidden_words:
            return False
        if re.match(r'^[+-]?\d+$', name):
            return False
        return True