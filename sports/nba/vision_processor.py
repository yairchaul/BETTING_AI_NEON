import streamlit as st
import re
import pandas as pd

class NBAVisionProcessor:
    # Procesador visual específico para capturas de NBA
    
    def process_games(self, lines):
        games = []
        i = 0
        while i < len(lines) - 1:
            # Buscar patrón: equipo, spread, odds_spread, O/U, total, odds_total, moneyline
            # Ejemplo: "Memphis Grizzlies +3 -110 O 227.5 -112 +130"
            line = lines[i]
            parts = line.split()
            
            if len(parts) >= 7:
                try:
                    game = {
                        'home': ' '.join(parts[:-6]),
                        'spread': parts[-6],
                        'odds_spread': parts[-5],
                        'ou': parts[-4],
                        'total': parts[-3],
                        'odds_total': parts[-2],
                        'moneyline': parts[-1]
                    }
                    
                    # La siguiente línea debería ser el equipo visitante
                    if i + 1 < len(lines):
                        next_parts = lines[i+1].split()
                        if len(next_parts) >= 7:
                            game['away'] = ' '.join(next_parts[:-6])
                            game['away_spread'] = next_parts[-6]
                            game['away_odds_spread'] = next_parts[-5]
                            game['away_ou'] = next_parts[-4]
                            game['away_odds_total'] = next_parts[-2]
                            game['away_moneyline'] = next_parts[-1]
                            games.append(game)
                            i += 1
                except:
                    pass
            i += 1
        return games
