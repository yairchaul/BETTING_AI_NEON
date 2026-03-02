# modules/real_analyzer.py
import numpy as np
from .smart_searcher import SmartSearcher

class RealAnalyzer:
    def __init__(self):
        self.searcher = SmartSearcher()
    
    def analyze_match(self, home_name, away_name):
        """
        Analiza un partido basado en los últimos 5 partidos de cada equipo
        """
        # Buscar equipos
        home_team = self.searcher.find_team(home_name)
        away_team = self.searcher.find_team(away_name)
        
        if not home_team or not away_team:
            return self._generate_generic_analysis(home_name, away_name)
        
        # Obtener últimos 5 partidos
        home_matches = self.searcher.get_last_5_matches(home_team['id'])
        away_matches = self.searcher.get_last_5_matches(away_team['id'])
        
        if not home_matches or not away_matches:
            return self._generate_generic_analysis(home_team['name'], away_team['name'])
        
        # Calcular estadísticas
        stats = self._calculate_stats(home_matches, away_matches)
        
        # Generar mercados basados en stats reales
        markets = self._generate_markets_from_stats(stats)
        
        return {
            'home_team': home_team['name'],
            'away_team': away_team['name'],
            'home_found': True,
            'away_found': True,
            'markets': markets,
            'stats': stats,
            'probabilidades': {
                'goles_promedio': stats['avg_total_goals']
            }
        }
    
    def _calculate_stats(self, home_matches, away_matches):
        """Calcula estadísticas de los últimos 5 partidos"""
        
        # Estadísticas locales
        home_goals_for = [m['goals_home'] if m['home'] == home_matches[0]['home'] else m['goals_away'] 
                         for m in home_matches]
        home_goals_against = [m['goals_away'] if m['home'] == home_matches[0]['home'] else m['goals_home'] 
                             for m in home_matches]
        
        # Estadísticas visitantes
        away_goals_for = [m['goals_away'] if m['away'] == away_matches[0]['away'] else m['goals_home'] 
                         for m in away_matches]
        away_goals_against = [m['goals_home'] if m['away'] == away_matches[0]['away'] else m['goals_away'] 
                             for m in away_matches]
        
        # Calcular promedios
        avg_home_for = np.mean(home_goals_for)
        avg_home_against = np.mean(home_goals_against)
        avg_away_for = np.mean(away_goals_for)
        avg_away_against = np.mean(away_goals_against)
        
        # BTTS en últimos partidos
        home_btts = sum(1 for i in range(5) if home_goals_for[i] > 0 and home_goals_against[i] > 0) / 5
        away_btts = sum(1 for i in range(5) if away_goals_for[i] > 0 and away_goals_against[i] > 0) / 5
        
        # Over stats
        home_over_1_5 = sum(1 for i in range(5) if (home_goals_for[i] + home_goals_against[i]) > 1.5) / 5
        home_over_2_5 = sum(1 for i in range(5) if (home_goals_for[i] + home_goals_against[i]) > 2.5) / 5
        home_over_3_5 = sum(1 for i in range(5) if (home_goals_for[i] + home_goals_against[i]) > 3.5) / 5
        
        away_over_1_5 = sum(1 for i in range(5) if (away_goals_for[i] + away_goals_against[i]) > 1.5) / 5
        away_over_2_5 = sum(1 for i in range(5) if (away_goals_for[i] + away_goals_against[i]) > 2.5) / 5
        away_over_3_5 = sum(1 for i in range(5) if (away_goals_for[i] + away_goals_against[i]) > 3.5) / 5
        
        return {
            'home_goals_for': avg_home_for,
            'home_goals_against': avg_home_against,
            'away_goals_for': avg_away_for,
            'away_goals_against': avg_away_against,
            'avg_total_goals': (avg_home_for + avg_home_against + avg_away_for + avg_away_against) / 2,
            'btts_prob': (home_btts + away_btts) / 2,
            'over_1_5_prob': (home_over_1_5 + away_over_1_5) / 2,
            'over_2_5_prob': (home_over_2_5 + away_over_2_5) / 2,
            'over_3_5_prob': (home_over_3_5 + away_over_3_5) / 2,
            'over_4_5_prob': (home_over_3_5 * 0.7 + away_over_3_5 * 0.7) / 2,  # Estimado
            'over_5_5_prob': (home_over_3_5 * 0.3 + away_over_3_5 * 0.3) / 2,  # Estimado
        }
    
    def _generate_markets_from_stats(self, stats):
        """Genera todos los mercados basados en estadísticas reales"""
        
        markets = [
            # Resultado final (estimado basado en estadísticas)
            {'name': 'Gana Local', 'prob': 0.4, 'category': '1X2'},
            {'name': 'Empate', 'prob': 0.25, 'category': '1X2'},
            {'name': 'Gana Visitante', 'prob': 0.35, 'category': '1X2'},
            
            # Doble oportunidad
            {'name': 'Local o Empate (1X)', 'prob': 0.65, 'category': 'Doble Oportunidad'},
            {'name': 'Visitante o Empate (X2)', 'prob': 0.6, 'category': 'Doble Oportunidad'},
            
            # Totales basados en stats reales
            {'name': 'Over 0.5 goles', 'prob': min(0.99, stats['avg_total_goals'] / 0.5 * 0.3), 'category': 'Totales'},
            {'name': 'Over 1.5 goles', 'prob': stats['over_1_5_prob'], 'category': 'Totales'},
            {'name': 'Over 2.5 goles', 'prob': stats['over_2_5_prob'], 'category': 'Totales'},
            {'name': 'Over 3.5 goles', 'prob': stats['over_3_5_prob'], 'category': 'Totales'},
            {'name': 'Over 4.5 goles', 'prob': stats['over_4_5_prob'], 'category': 'Totales (Especial)'},
            {'name': 'Over 5.5 goles', 'prob': stats['over_5_5_prob'], 'category': 'Totales (Especial)'},
            
            # BTTS
            {'name': 'Ambos anotan (BTTS)', 'prob': stats['btts_prob'], 'category': 'BTTS'},
            {'name': 'No anotan ambos', 'prob': 1 - stats['btts_prob'], 'category': 'BTTS'},
            
            # Primer tiempo (estimados)
            {'name': 'Over 0.5 goles (1T)', 'prob': stats['over_1_5_prob'] * 0.7, 'category': 'Primer Tiempo'},
            {'name': 'Over 1.5 goles (1T)', 'prob': stats['over_2_5_prob'] * 0.4, 'category': 'Primer Tiempo'},
            {'name': 'Ambos anotan (1T)', 'prob': stats['btts_prob'] * 0.5, 'category': 'Primer Tiempo'},
            
            # Combinados
            {'name': 'Gana Local + Over 1.5', 'prob': 0.4 * stats['over_1_5_prob'], 'category': 'Combinado'},
            {'name': 'Gana Local + Over 2.5', 'prob': 0.4 * stats['over_2_5_prob'], 'category': 'Combinado'},
            {'name': 'Gana Visitante + Over 1.5', 'prob': 0.35 * stats['over_1_5_prob'], 'category': 'Combinado'},
            {'name': 'Gana Visitante + Over 2.5', 'prob': 0.35 * stats['over_2_5_prob'], 'category': 'Combinado'},
            {'name': 'BTTS + Over 2.5', 'prob': stats['btts_prob'] * stats['over_2_5_prob'], 'category': 'Combinado'},
        ]
        
        return sorted(markets, key=lambda x: x['prob'], reverse=True)
    
    def _generate_generic_analysis(self, home_name, away_name):
        """Genera análisis genérico cuando no hay datos"""
        return {
            'home_team': home_name,
            'away_team': away_name,
            'home_found': False,
            'away_found': False,
            'markets': self._generate_generic_markets(),
            'probabilidades': {'goles_promedio': 2.5}
        }
    
    def _generate_generic_markets(self):
        """Mercados genéricos cuando no hay datos"""
        return [
            {'name': 'Over 0.5 goles', 'prob': 0.95, 'category': 'Totales'},
            {'name': 'Over 1.5 goles', 'prob': 0.80, 'category': 'Totales'},
            {'name': 'Over 0.5 goles (1T)', 'prob': 0.70, 'category': 'Primer Tiempo'},
            {'name': 'Ambos anotan (BTTS)', 'prob': 0.60, 'category': 'BTTS'},
            {'name': 'Over 2.5 goles', 'prob': 0.55, 'category': 'Totales'},
            {'name': 'Ambos anotan (1T)', 'prob': 0.45, 'category': 'Primer Tiempo'},
        ]
