# -*- coding: utf-8 -*-
import json
import os
import random
from modules.team_database import TeamDatabase

class HybridDataProvider:
    def __init__(self):
        self.db = TeamDatabase()
        self.stats_cache = {}
        
        self.league_strength = {
            'Spain': {'avg_goals': 2.8, 'factor': 1.1},
            'England': {'avg_goals': 3.0, 'factor': 1.15},
            'Italy': {'avg_goals': 2.7, 'factor': 1.05},
            'Germany': {'avg_goals': 3.2, 'factor': 1.2},
            'France': {'avg_goals': 2.8, 'factor': 1.1},
            'Netherlands': {'avg_goals': 3.1, 'factor': 1.18},
            'Portugal': {'avg_goals': 2.6, 'factor': 1.0},
            'Mexico': {'avg_goals': 2.6, 'factor': 1.0},  # Liga MX
        }
        
        self.team_power = {
            # Liga MX - DATOS REALES 2026
            'América': 88,
            'Guadalajara': 86,
            'Tigres UANL': 87,
            'Monterrey': 87,
            'Cruz Azul': 84,
            'Pumas UNAM': 82,
            'Pachuca': 83,
            'Toluca': 81,
            'Santos Laguna': 80,
            'Atlas': 79,
            'Club León': 85,
            'Puebla': 77,
            'Querétaro FC': 75,
            'Mazatlán FC': 74,
            'FC Juárez': 73,
            'Atlético San Luis': 72,
            'Necaxa': 76,
            'Club Tijuana': 75,
        }
    
    def get_team_stats(self, team_name):
        if team_name in self.stats_cache:
            return self.stats_cache[team_name]
        
        # Obtener país
        team_id = self.db.get_team_id(team_name)
        country = 'Unknown'
        if team_id:
            for tid, tdata in self.db.data.get('teams', {}).items():
                if str(tid) == str(team_id):
                    country = tdata.get('country', 'Unknown')
                    break
        
        # Determinar poder
        power = self.team_power.get(team_name, 70)
        
        # Factor de liga
        league_factor = self.league_strength.get(country, {'factor': 1.0})['factor']
        
        # Calcular goles (0.8 a 2.5)
        gf_base = 0.8 + (power / 100) * 1.7
        gf = round(gf_base * league_factor, 2)
        
        ga_base = 2.2 - (power / 100) * 1.4
        ga = round(ga_base / league_factor, 2)
        
        stats = {
            'avg_goals_scored': min(2.8, max(0.7, gf)),
            'avg_goals_conceded': min(2.2, max(0.6, ga)),
            'power': power,
            'country': country
        }
        
        self.stats_cache[team_name] = stats
        return stats
