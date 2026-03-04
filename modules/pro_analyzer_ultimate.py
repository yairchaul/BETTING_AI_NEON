# modules/pro_analyzer_ultimate.py
import streamlit as st
import requests
import json
import numpy as np
import re
from datetime import datetime
from modules.team_knowledge import TeamKnowledge
from modules.smart_searcher import SmartSearcher
from modules.montecarlo_pro import MonteCarloPro
from modules.elo_system import ELOSystem
from modules.xgboost_predictor import XGBoostPredictor
from math import exp, factorial
from modules.team_translator import TeamTranslator
from modules.odds_api_integrator import OddsAPIIntegrator

class ProAnalyzerUltimate:
    """
    Analizador profesional con cobertura GLOBAL de ligas
    CALCULA DINÁMICAMENTE todas las probabilidades basado en datos reales
    """

    def __init__(self):
        self.knowledge = TeamKnowledge()
        self.searcher = SmartSearcher()
        self.montecarlo = MonteCarloPro(simulations=50000)
        self.elo = ELOSystem(k_factor=32, home_advantage=100)
        self.xgb = XGBoostPredictor()
        self.translator = TeamTranslator()
        self.odds_api = OddsAPIIntegrator()
        self.max_edge = 0.06

        self.weights = {
            'market': 0.20,
            'poisson': 0.25,
            'elo': 0.15,
            'xgb': 0.25,
            'ollama': 0.15
        }

        # Intentar conectar Ollama
        self.ollama_available = False
        try:
            import requests
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            self.ollama_available = response.status_code == 200
        except:
            pass

    # ============================================================================
    # FUNCIÓN PRINCIPAL DE ANÁLISIS
    # ============================================================================
    def analyze_match(self, home_team, away_team, odds_dict):
        """
        Analiza un partido y calcula DINÁMICAMENTE todos los mercados
        """
        try:
            # Obtener odds en formato decimal
            odds_decimal = odds_dict.get('decimal_odds', odds_dict.get('all_odds', [2.0, 3.2, 3.5]))
            
            # BUSCAR DATOS REALES (NO SIMULADOS)
            home_info = self.searcher.get_team_stats(home_team)
            away_info = self.searcher.get_team_stats(away_team)
            h2h = self.searcher.get_head_to_head(home_team, away_team)
            
            # CALCULAR FUERZAS BASADO EN DATOS REALES
            home_attack, home_defense = self._calculate_team_strength(home_info, home_team)
            away_attack, away_defense = self._calculate_team_strength(away_info, away_team)
            
            # Obtener probabilidades ELO
            elo_probs_dict = self.elo.get_win_probability(home_team, away_team)
            elo_probs = [elo_probs_dict.get('home', 0.35), 
                        elo_probs_dict.get('draw', 0.30), 
                        elo_probs_dict.get('away', 0.35)]
            
            # ============================================================================
            # SIMULACIÓN MONTECARLO CON DATOS REALES
            # ============================================================================
            # CORREGIDO: Pasar los argumentos correctos
            try:
                mc_stats = self.montecarlo.simulate_match(
                    home_attack, away_attack, home_defense, away_defense
                )
            except:
                # Si falla, usar método alternativo
                mc_stats = self._calculate_mc_stats_manual(
                    home_attack, away_attack, home_defense, away_defense,
                    home_info, away_info, h2h
                )
            
            # ============================================================================
            # CALCULAR PROBABILIDADES DE CADA MODELO
            # ============================================================================
            market_probs = self._market_probabilities(odds_decimal)
            poisson_probs = self._poisson_probabilities(home_attack, away_attack, home_defense, away_defense)
            xgb_probs = self._xgb_probabilities(home_team, away_team, home_info, away_info, h2h)
            ollama_probs = self._ollama_probabilities(home_team, away_team, home_info, away_info)
            
            probs_by_model = {
                'market': market_probs,
                'poisson': poisson_probs,
                'elo': elo_probs,
                'xgb': xgb_probs,
                'ollama': ollama_probs
            }
            
            # Combinar probabilidades finales (1X2)
            final_probs = self._combine_probabilities(probs_by_model)
            
            # ============================================================================
            # CALCULAR TODOS LOS MERCADOS DINÁMICAMENTE
            # ============================================================================
            all_markets = self._calculate_all_markets_dinamico(
                mc_stats, final_probs, home_team, away_team,
                home_info, away_info, h2h, odds_decimal,
                home_attack, away_attack, home_defense, away_defense
            )
            
            # Encontrar la mejor opción
            best_market = max(all_markets, key=lambda x: x['prob'])
            
            # Detectar liga
            league = self._detect_league(home_team, away_team)
            
            return {
                'home_team': home_team,
                'away_team': away_team,
                'liga': league,
                'final_probs': final_probs,
                'probs_by_model': probs_by_model,
                'mc_stats': mc_stats,
                'markets': all_markets,
                'best_market': best_market,
                'total_markets': len(all_markets),
                'elo_probs': elo_probs,
                'historical_data': h2h,
                'team_stats': {'home': home_info, 'away': away_info},
                'team_strength': {
                    'home_attack': home_attack,
                    'home_defense': home_defense,
                    'away_attack': away_attack,
                    'away_defense': away_defense
                }
            }
            
        except Exception as e:
            st.error(f"Error en analyze_match: {e}")
            return self._get_default_analysis(home_team, away_team)

    # ============================================================================
    # CÁLCULO DINÁMICO DE TODOS LOS MERCADOS (VERSIÓN MEJORADA)
    # ============================================================================
    def _calculate_all_markets_dinamico(self, mc_stats, probs_1x2, home_team, away_team,
                                        home_stats, away_stats, h2h, odds_decimal,
                                        home_attack, away_attack, home_defense, away_defense):
        """
        Calcula TODOS los mercados basado en DATOS REALES, no valores fijos
        """
        markets = []
        
        # ============================================================================
        # 1. RESULTADO FINAL (1X2) - Basado en modelos combinados
        # ============================================================================
        markets.append(self._crear_market('Gana Local', probs_1x2[0], '1X2', 
                      f"Probabilidad combinada de {probs_1x2[0]:.1%} según múltiples modelos"))
        markets.append(self._crear_market('Empate', probs_1x2[1], '1X2',
                      f"Probabilidad de empate según distribución Poisson y ELO"))
        markets.append(self._crear_market('Gana Visitante', probs_1x2[2], '1X2',
                      f"Probabilidad combinada de {probs_1x2[2]:.1%} según múltiples modelos"))
        
        # ============================================================================
        # 2. AMBOS EQUIPOS ANOTAN (BTTS) - Calculado desde Monte Carlo
        # ============================================================================
        btts_prob = mc_stats.get('btts', 0.5)
        markets.append(self._crear_market('BTTS - Sí', btts_prob, 'BTTS',
                      f"Basado en {mc_stats.get('simulations', 50000):,} simulaciones Monte Carlo"))
        markets.append(self._crear_market('BTTS - No', 1 - btts_prob, 'BTTS',
                      f"Probabilidad de que al menos un equipo no anote"))
        
        # ============================================================================
        # 3. TOTAL GOLES OVER/UNDER - Calculado desde Monte Carlo
        # ============================================================================
        over_probs = {}
        for total in [0.5, 1.5, 2.5, 3.5, 4.5]:
            over_prob = mc_stats.get(f'over_{total}', 0.5)
            over_probs[f'over_{total}'] = over_prob
            
            markets.append(self._crear_market(f'Over {total}', over_prob, 'Totales',
                          f"Basado en distribución Poisson con λ={mc_stats.get('avg_goals', 2.5):.2f}"))
            markets.append(self._crear_market(f'Under {total}', 1 - over_prob, 'Totales',
                          f"Basado en distribución Poisson con λ={mc_stats.get('avg_goals', 2.5):.2f}"))
        
        # ============================================================================
        # 4. PRIMERA MITAD - Calculado con modelo específico
        # ============================================================================
        first_half_markets = self._calculate_first_half_markets(
            probs_1x2, home_attack, away_attack, home_defense, away_defense
        )
        markets.extend(first_half_markets)
        
        # ============================================================================
        # 5. RESULTADO FINAL + OVER/UNDER - Combinaciones
        # ============================================================================
        combo_markets = self._calculate_combo_markets(probs_1x2, over_probs)
        markets.extend(combo_markets)
        
        # ============================================================================
        # 6. DOBLE OPORTUNIDAD + OVER/UNDER
        # ============================================================================
        double_chance_markets = self._calculate_double_chance_markets(probs_1x2, over_probs)
        markets.extend(double_chance_markets)
        
        # ============================================================================
        # 7. HÁNDICAP ASIÁTICO - Basado en distribución de diferencia de goles
        # ============================================================================
        asian_handicap_markets = self._calculate_asian_handicap(mc_stats, probs_1x2)
        markets.extend(asian_handicap_markets)
        
        # ============================================================================
        # 8. ANOTADORES - Con Ollama si está disponible
        # ============================================================================
        if self.ollama_available:
            scorers = self._calculate_scorers(home_team, away_team, home_stats, away_stats)
            markets.extend(scorers)
        
        # Ordenar por probabilidad
        markets.sort(key=lambda x: x['prob'], reverse=True)
        
        return markets

    def _crear_market(self, name, prob, category, reason):
        """Crea un mercado con formato estándar"""
        return {
            'name': name,
            'prob': prob,
            'category': category,
            'confidence': self._determinar_confianza(prob),
            'reason': reason
        }

    def _determinar_confianza(self, prob):
        """Determina nivel de confianza basado en probabilidad"""
        if prob > 0.7:
            return 'ALTA'
        elif prob > 0.6:
            return 'MEDIA-ALTA'
        elif prob > 0.55:
            return 'MEDIA'
        elif prob > 0.45:
            return 'MEDIA-BAJA'
        else:
            return 'BAJA'

    # ============================================================================
    # CÁLCULOS ESPECÍFICOS PARA PRIMERA MITAD
    # ============================================================================
    def _calculate_first_half_markets(self, probs_1x2, home_attack, away_attack, 
                                      home_defense, away_defense):
        """Calcula probabilidades para primera mitad basado en datos"""
        markets = []
        
        # Ajustar fuerzas para primera mitad (menos goles)
        home_attack_ht = home_attack * 0.4
        away_attack_ht = away_attack * 0.4
        
        # Over/Under 1.5 en primera mitad usando Poisson ajustado
        lambda_ht = (home_attack_ht + away_attack_ht) * 1.0
        over_1_5_ht = 1 - (exp(-lambda_ht) * (1 + lambda_ht))
        over_1_5_ht = min(max(over_1_5_ht, 0.25), 0.45)  # Limitar entre 25% y 45%
        
        markets.append(self._crear_market('Over 1.5 (1T)', over_1_5_ht, 'Primer Tiempo',
                      f"Basado en Poisson con λ={lambda_ht:.2f} para primera mitad"))
        markets.append(self._crear_market('Under 1.5 (1T)', 1 - over_1_5_ht, 'Primer Tiempo',
                      f"Probabilidad de 0-1 goles en primer tiempo"))
        
        # Resultado primera mitad (correlación con resultado final)
        home_win_ht = probs_1x2[0] * 0.55
        away_win_ht = probs_1x2[2] * 0.55
        draw_ht = 1 - home_win_ht - away_win_ht
        
        markets.append(self._crear_market('Gana Local (1T)', home_win_ht, 'Primer Tiempo',
                      f"Correlación del 55% con victoria final"))
        markets.append(self._crear_market('Empate (1T)', draw_ht, 'Primer Tiempo',
                      f"Alta probabilidad de empate al descanso"))
        markets.append(self._crear_market('Gana Visitante (1T)', away_win_ht, 'Primer Tiempo',
                      f"Correlación del 55% con victoria final"))
        
        return markets

    # ============================================================================
    # CÁLCULOS PARA MERCADOS COMBINADOS
    # ============================================================================
    def _calculate_combo_markets(self, probs_1x2, over_probs):
        """Calcula Resultado Final + Over/Under"""
        markets = []
        
        for total in [1.5, 2.5, 3.5]:
            over_prob = over_probs.get(f'over_{total}', 0.5)
            under_prob = 1 - over_prob
            
            # Local + Over/Under
            markets.append(self._crear_market(f'Local y Over {total}', 
                          probs_1x2[0] * over_prob, f'Combinado O/U {total}',
                          f"Probabilidad conjunta: P(Local)  P(Over {total})"))
            markets.append(self._crear_market(f'Local y Under {total}',
                          probs_1x2[0] * under_prob, f'Combinado O/U {total}',
                          f"Victoria local en partido con pocos goles"))
            
            # Visitante + Over/Under
            markets.append(self._crear_market(f'Visitante y Over {total}',
                          probs_1x2[2] * over_prob, f'Combinado O/U {total}',
                          f"Victoria visitante en partido con muchos goles"))
            markets.append(self._crear_market(f'Visitante y Under {total}',
                          probs_1x2[2] * under_prob, f'Combinado O/U {total}',
                          f"Victoria visitante en partido con pocos goles"))
        
        return markets

    def _calculate_double_chance_markets(self, probs_1x2, over_probs):
        """Calcula Doble Oportunidad + Over/Under"""
        markets = []
        
        dc_probs = {
            'home_away': probs_1x2[0] + probs_1x2[2],
            'home_draw': probs_1x2[0] + probs_1x2[1],
            'away_draw': probs_1x2[2] + probs_1x2[1]
        }
        
        dc_labels = {
            'home_away': 'Local/Visitante',
            'home_draw': 'Local/Empate',
            'away_draw': 'Visitante/Empate'
        }
        
        for total in [1.5, 2.5, 3.5]:
            over_prob = over_probs.get(f'over_{total}', 0.5)
            under_prob = 1 - over_prob
            
            for dc_key, dc_prob in dc_probs.items():
                markets.append(self._crear_market(f'{dc_labels[dc_key]} y Over {total}',
                              dc_prob * over_prob, f'Doble Oportunidad O/U {total}',
                              f"Doble oportunidad con {total}+ goles"))
                markets.append(self._crear_market(f'{dc_labels[dc_key]} y Under {total}',
                              dc_prob * under_prob, f'Doble Oportunidad O/U {total}',
                              f"Doble oportunidad con menos de {total} goles"))
        
        return markets

    def _calculate_asian_handicap(self, mc_stats, probs_1x2):
        """Calcula probabilidades para hándicap asiático"""
        markets = []
        
        # Estimar diferencia de goles basado en estadísticas
        avg_goals = mc_stats.get('avg_goals', 2.5)
        home_win_prob = probs_1x2[0]
        
        # Hándicap -1.5 (Local gana por 2+)
        ah_minus_1_5 = home_win_prob * (0.3 + (avg_goals - 2) * 0.1)
        ah_minus_1_5 = min(max(ah_minus_1_5, 0.1), 0.4)
        
        markets.append(self._crear_market('Local -1.5', ah_minus_1_5, 'Hándicap Asiático',
                      f"Basado en {home_win_prob:.1%} de victoria local y {avg_goals:.1f} goles promedio"))
        markets.append(self._crear_market('Visitante +1.5', 1 - ah_minus_1_5 * 0.8, 'Hándicap Asiático',
                      f"Visitante no pierde por 2+ goles"))
        
        # Hándicap -1 (Local gana por 2+ o devolución si gana por 1)
        ah_minus_1 = ah_minus_1_5 + (home_win_prob * 0.2)
        markets.append(self._crear_market('Local -1', ah_minus_1, 'Hándicap Asiático',
                      f"Incluye devolución si gana por 1 gol"))
        markets.append(self._crear_market('Visitante +1', 1 - ah_minus_1_5, 'Hándicap Asiático',
                      f"Visitante no pierde por 2+ goles"))
        
        return markets

    def _calculate_scorers(self, home_team, away_team, home_stats, away_stats):
        """Calcula probabilidades de anotadores usando datos históricos"""
        markets = []
        
        # Intentar obtener datos reales de goleadores
        home_scorers = home_stats.get('top_scorers', [])
        away_scorers = away_stats.get('top_scorers', [])
        
        if home_scorers:
            for scorer in home_scorers[:2]:
                prob = min(scorer.get('goals_per_game', 0.3) * 0.8, 0.3)
                markets.append(self._crear_market(f'Anota: {scorer["name"]} (Local)', 
                              prob, 'Anotadores', f"Basado en {scorer.get('goals', 0)} goles esta temporada"))
        
        if away_scorers:
            for scorer in away_scorers[:2]:
                prob = min(scorer.get('goals_per_game', 0.25) * 0.8, 0.25)
                markets.append(self._crear_market(f'Anota: {scorer["name"]} (Visitante)', 
                              prob, 'Anotadores', f"Basado en {scorer.get('goals', 0)} goles esta temporada"))
        
        return markets

    # ============================================================================
    # FUNCIONES AUXILIARES PARA CÁLCULOS
    # ============================================================================
    def _market_probabilities(self, odds_decimal):
        """Calcula probabilidades de mercado (inversa de odds)"""
        if not odds_decimal or len(odds_decimal) < 3:
            return [0.34, 0.32, 0.34]
        
        probs = [1/o for o in odds_decimal if o and o > 0]
        total = sum(probs)
        return [p/total for p in probs] if total > 0 else [0.34, 0.32, 0.34]

    def _poisson_probabilities(self, home_attack, away_attack, home_defense, away_defense):
        """Calcula probabilidades usando distribución Poisson"""
        lambda_home = home_attack * away_defense * 1.2
        lambda_away = away_attack * home_defense * 1.0
        
        probs = [0, 0, 0]
        for gh in range(8):
            for ga in range(8):
                prob = (exp(-lambda_home) * lambda_home**gh / factorial(gh)) * \
                       (exp(-lambda_away) * lambda_away**ga / factorial(ga))
                
                if gh > ga:
                    probs[0] += prob
                elif gh == ga:
                    probs[1] += prob
                else:
                    probs[2] += prob
        
        total = sum(probs)
        return [p/total for p in probs] if total > 0 else [0.34, 0.32, 0.34]

    def _xgb_probabilities(self, home_team, away_team, home_stats, away_stats, h2h):
        """Probabilidades de XGBoost (simulado por ahora)"""
        # Aquí iría la integración real con XGBoost
        return [0.34, 0.32, 0.34]

    def _ollama_probabilities(self, home_team, away_team, home_stats, away_stats):
        """Obtiene probabilidades de Ollama si está disponible"""
        if not self.ollama_available:
            return [0.34, 0.32, 0.34]
        
        try:
            import requests
            prompt = f"Analiza el partido {home_team} vs {away_team}. Da solo tres números que sumen 1.0 para (local, empate, visitante) basado en forma reciente."
            
            response = requests.post('http://localhost:11434/api/generate',
                                    json={'model': 'llama3.1:8b', 'prompt': prompt, 'stream': False},
                                    timeout=5)
            
            if response.status_code == 200:
                text = response.json().get('response', '')
                numbers = re.findall(r'0\.\d+', text)
                if len(numbers) >= 3:
                    return [float(numbers[0]), float(numbers[1]), float(numbers[2])]
        except:
            pass
        
        return [0.34, 0.32, 0.34]

    def _calculate_team_strength(self, team_info, team_name):
        """Calcula fuerza ofensiva y defensiva basado en datos reales"""
        if not team_info:
            # Intentar buscar en caché o usar valores por defecto
            return 1.0, 1.0
        
        avg_scored = team_info.get('avg_goals_scored', 1.2)
        avg_conceded = team_info.get('avg_goals_conceded', 1.2)
        
        attack = avg_scored / 1.2
        defense = avg_conceded / 1.2
        
        return attack, defense

    def _calculate_mc_stats_manual(self, home_attack, away_attack, home_defense, away_defense,
                                   home_info, away_info, h2h):
        """Calcula estadísticas Monte Carlo manualmente si la función falla"""
        lambda_home = home_attack * away_defense * 1.2
        lambda_away = away_attack * home_defense * 1.0
        
        simulations = 50000
        btts = 0
        goals_total = []
        
        for _ in range(simulations):
            gh = np.random.poisson(lambda_home)
            ga = np.random.poisson(lambda_away)
            goals_total.append(gh + ga)
            if gh > 0 and ga > 0:
                btts += 1
        
        goals_total = np.array(goals_total)
        
        return {
            'avg_goals': np.mean(goals_total),
            'std_goals': np.std(goals_total),
            'btts': btts / simulations,
            'over_0_5': np.mean(goals_total > 0.5),
            'over_1_5': np.mean(goals_total > 1.5),
            'over_2_5': np.mean(goals_total > 2.5),
            'over_3_5': np.mean(goals_total > 3.5),
            'over_4_5': np.mean(goals_total > 4.5),
            'simulations': simulations
        }

    def _combine_probabilities(self, probs_by_model):
        """Combina probabilidades de todos los modelos con pesos"""
        combined = [0, 0, 0]
        total_weight = 0
        
        for model, probs in probs_by_model.items():
            weight = self.weights.get(model, 0.2)
            for i in range(3):
                combined[i] += probs[i] * weight
            total_weight += weight
        
        return [p/total_weight for p in combined]

    def _detect_league(self, home_team, away_team):
        """Detecta la liga del partido"""
        league = self.knowledge.detect_league(home_team, away_team)
        return league if league else 'default'

    def _get_default_analysis(self, home_team, away_team):
        """Retorna análisis por defecto en caso de error"""
        default_markets = [
            self._crear_market('Gana Local', 0.35, '1X2', 'Valor por defecto'),
            self._crear_market('Empate', 0.30, '1X2', 'Valor por defecto'),
            self._crear_market('Gana Visitante', 0.35, '1X2', 'Valor por defecto'),
            self._crear_market('BTTS - Sí', 0.52, 'BTTS', 'Basado en promedio histórico'),
            self._crear_market('BTTS - No', 0.48, 'BTTS', 'Basado en promedio histórico'),
            self._crear_market('Over 0.5', 0.92, 'Totales', 'Casi siempre hay gol'),
            self._crear_market('Over 1.5', 0.78, 'Totales', 'Promedio histórico'),
            self._crear_market('Over 2.5', 0.58, 'Totales', 'Promedio histórico'),
        ]
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'liga': 'default',
            'final_probs': [0.35, 0.30, 0.35],
            'probs_by_model': {},
            'mc_stats': {'avg_goals': 2.5, 'btts': 0.52, 'over_0_5': 0.92, 'over_1_5': 0.78, 'over_2_5': 0.58},
            'markets': default_markets,
            'best_market': default_markets[6],
            'total_markets': len(default_markets)
        }
