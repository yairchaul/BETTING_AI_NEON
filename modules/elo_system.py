# modules/elo_system.py
import numpy as np
import pandas as pd
from datetime import datetime
import streamlit as st

class ELOSystem:
    """
    Sistema de rating ELO para equipos de fútbol
    Basado en el sistema de la FIFA pero adaptado para apuestas
    """
    
    def __init__(self, k_factor=32, home_advantage=100):
        self.ratings = {}  # Dict[team_name, rating]
        self.k_factor = k_factor
        self.home_advantage = home_advantage
        self.history = []  # Historial de cambios
    
    def get_rating(self, team, default=1500):
        """Obtiene el rating de un equipo, si no existe lo crea con valor por defecto"""
        if team not in self.ratings:
            self.ratings[team] = default
        return self.ratings[team]
    
    def expected_score(self, rating_a, rating_b, home=False):
        """
        Calcula el puntaje esperado para el equipo A contra el equipo B
        Fórmula ELO estándar: E = 1 / (1 + 10^((RB - RA)/400))
        """
        rating_adj = rating_a
        if home:
            rating_adj += self.home_advantage
        
        return 1 / (1 + 10 ** ((rating_b - rating_adj) / 400))
    
    def update_ratings(self, home_team, away_team, home_goals, away_goals, timestamp=None):
        """
        Actualiza los ratings después de un partido
        """
        # Obtener ratings actuales
        rating_home = self.get_rating(home_team)
        rating_away = self.get_rating(away_team)
        
        # Resultado real (1 = local gana, 0.5 = empate, 0 = visitante gana)
        if home_goals > away_goals:
            actual_home = 1
            actual_away = 0
        elif home_goals == away_goals:
            actual_home = 0.5
            actual_away = 0.5
        else:
            actual_home = 0
            actual_away = 1
        
        # Puntaje esperado (considerando ventaja local)
        expected_home = self.expected_score(rating_home, rating_away, home=True)
        expected_away = 1 - expected_home
        
        # Factor K ajustado por diferencia de goles (para dar más peso a goleadas)
        goal_diff = abs(home_goals - away_goals)
        k_adj = self.k_factor * (1 + 0.2 * goal_diff)  # Hasta 20% más por cada gol de diferencia
        
        # Actualizar ratings
        new_rating_home = rating_home + k_adj * (actual_home - expected_home)
        new_rating_away = rating_away + k_adj * (actual_away - expected_away)
        
        self.ratings[home_team] = new_rating_home
        self.ratings[away_team] = new_rating_away
        
        # Guardar en historial
        self.history.append({
            'date': timestamp or datetime.now(),
            'home': home_team,
            'away': away_team,
            'home_goals': home_goals,
            'away_goals': away_goals,
            'rating_home_before': rating_home,
            'rating_away_before': rating_away,
            'rating_home_after': new_rating_home,
            'rating_away_after': new_rating_away,
            'expected_home': expected_home,
            'actual_home': actual_home,
            'k_factor_used': k_adj
        })
        
        return {
            'home_new': new_rating_home,
            'away_new': new_rating_away,
            'expected_home': expected_home,
            'expected_away': expected_away
        }
    
    def get_win_probability(self, home_team, away_team):
        """
        Calcula probabilidad de victoria basada solo en ELO
        """
        rating_home = self.get_rating(home_team)
        rating_away = self.get_rating(away_team)
        
        expected_home = self.expected_score(rating_home, rating_away, home=True)
        
        # Probabilidades aproximadas (asumiendo que empate es el resto después de ajustar)
        # Esta es una simplificación, en realidad el empate tiene su propia distribución
        home_prob = expected_home * 0.9
        away_prob = (1 - expected_home) * 0.9
        draw_prob = 1 - home_prob - away_prob
        
        return {
            'home': home_prob,
            'draw': draw_prob,
            'away': away_prob
        }
    
    def get_top_teams(self, n=10):
        """Devuelve los n equipos con mejor rating"""
        sorted_teams = sorted(self.ratings.items(), key=lambda x: x[1], reverse=True)
        return sorted_teams[:n]
    
    def save_ratings(self, filepath='data/elo_ratings.json'):
        """Guarda los ratings en un archivo"""
        import json
        with open(filepath, 'w') as f:
            json.dump({
                'ratings': self.ratings,
                'history': self.history[-1000:]  # Guardar últimos 1000 cambios
            }, f, indent=2, default=str)
    
    def load_ratings(self, filepath='data/elo_ratings.json'):
        """Carga ratings desde un archivo"""
        import json
        import os
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.ratings = data.get('ratings', {})
                self.history = data.get('history', [])
                
    def get_win_probability(self, home_team, away_team):
    """
    Calcula probabilidad de victoria basada solo en ELO (VERSIÓN CORREGIDA)
    """
    rating_home = self.get_rating(home_team)
    rating_away = self.get_rating(away_team)
    
    expected_home = self.expected_score(rating_home, rating_away, home=True)
    
    # Ajuste: El empate no es simplemente el resto
    # En fútbol, el empate tiene su propia probabilidad basada en la liga
    # Usamos una fórmula más realista
    
    # Probabilidad de empate base (mayor cuando equipos están parejos)
    rating_diff = abs(rating_home - rating_away)
    draw_base = max(0.20, 0.30 - (rating_diff / 2000))  # Entre 20% y 30%
    
    # Ajustar según ventaja local
    home_adj = expected_home * 0.85
    away_adj = (1 - expected_home) * 0.85
    
    # Normalizar
    total = home_adj + away_adj + draw_base
    home_prob = home_adj / total
    draw_prob = draw_base / total
    away_prob = away_adj / total
    
    return {
        'home': home_prob,
        'draw': draw_prob,
        'away': away_prob
    }
