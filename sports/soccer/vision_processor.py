import streamlit as st
import re

class SoccerVisionProcessor:
    # Procesador visual específico para capturas de fútbol
    
    def process_matches(self, lines):
        matches = []
        i = 0
        while i < len(lines) - 2:
            # Buscar patrón: Local, odds_local, empate, odds_empate, visitante, odds_visitante
            # Ejemplo: "Galatasaray +350 Empate +295 Liverpool -139"
            line = lines[i]
            parts = line.split()
            
            if len(parts) >= 6 and 'Empate' in line:
                try:
                    local_idx = 0
                    empate_idx = parts.index('Empate') if 'Empate' in parts else -1
                    
                    if empate_idx > 0:
                        match = {
                            'home': ' '.join(parts[:empate_idx-1]),
                            'odds_home': parts[empate_idx-1],
                            'away': ' '.join(parts[empate_idx+2:]),
                            'odds_away': parts[-1]
                        }
                        matches.append(match)
                except:
                    pass
            i += 1
        return matches
