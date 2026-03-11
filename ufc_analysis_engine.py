"""
Motor de análisis UFC - Predice ganador, método, round, finalización
"""
import random
import math

class UFCAnalysisEngine:
    """
    Analiza combates UFC usando simulación Monte Carlo
    Predice: ganador, método, round, probabilidad de finalización
    """
    
    def analizar_combate(self, combate):
        """
        Retorna análisis completo del combate
        """
        p1 = combate['peleador1']
        p2 = combate['peleador2']
        
        # ========================================
        # ESTIMAR PROBABILIDAD BASE
        # ========================================
        # Basado en récords (simplificado)
        record_p1 = self._parse_record(p1.get('record', '0-0-0'))
        record_p2 = self._parse_record(p2.get('record', '0-0-0'))
        
        total_p1 = record_p1['wins'] + record_p1['losses'] + record_p1['draws']
        total_p2 = record_p2['wins'] + record_p2['losses'] + record_p2['draws']
        
        if total_p1 > 0:
            win_rate_p1 = record_p1['wins'] / total_p1
        else:
            win_rate_p1 = 0.5
        
        if total_p2 > 0:
            win_rate_p2 = record_p2['wins'] / total_p2
        else:
            win_rate_p2 = 0.5
        
        # Normalizar
        total_win_rate = win_rate_p1 + win_rate_p2
        prob_p1 = win_rate_p1 / total_win_rate
        prob_p2 = win_rate_p2 / total_win_rate
        
        # ========================================
        # SIMULACIÓN MONTE CARLO (10,000 iteraciones)
        # ========================================
        resultados = []
        rondas_totales = 5 if 'Principal' in combate.get('tipo_tarjeta', '') else 3
        
        for _ in range(10000):
            # Determinar ganador
            ganador = 'p1' if random.random() < prob_p1 else 'p2'
            
            # Determinar método
            r = random.random()
            if r < 0.45:  # 45% KO/TKO
                metodo = 'KO/TKO'
                round_combate = random.randint(1, rondas_totales)
                finalizado = True
            elif r < 0.70:  # 25% sumisión
                metodo = 'Sumisión'
                round_combate = random.randint(1, rondas_totales)
                finalizado = True
            else:  # 30% decisión
                metodo = 'Decisión'
                round_combate = rondas_totales
                finalizado = False
            
            resultados.append({
                'ganador': ganador,
                'metodo': metodo,
                'round': round_combate,
                'finalizado': finalizado
            })
        
        # ========================================
        # ANÁLISIS ESTADÍSTICO
        # ========================================
        victorias_p1 = sum(1 for r in resultados if r['ganador'] == 'p1')
        victorias_p2 = 10000 - victorias_p1
        
        # Métodos
        metodos = {}
        for r in resultados:
            metodos[r['metodo']] = metodos.get(r['metodo'], 0) + 1
        
        # Rounds
        rounds = {}
        for r in resultados:
            rounds[r['round']] = rounds.get(r['round'], 0) + 1
        
        # Finalización
        finalizados = sum(1 for r in resultados if r['finalizado'])
        prob_finalizacion = finalizados / 10000
        
        # Round más probable
        round_probable = max(rounds, key=rounds.get)
        
        # Método más probable
        metodo_probable = max(metodos, key=metodos.get)
        
        return {
            'ganador': {
                p1['nombre']: victorias_p1 / 10000,
                p2['nombre']: victorias_p2 / 10000
            },
            'metodo_mas_probable': metodo_probable,
            'round_mas_probable': round_probable,
            'probabilidad_finalizacion': prob_finalizacion,
            'confianza': 'ALTA' if max(victorias_p1, victorias_p2) > 6000 else 'MEDIA',
            'detalle': {
                'metodos': {k: v/10000 for k, v in metodos.items()},
                'rounds': {k: v/10000 for k, v in rounds.items()}
            }
        }
    
    def _parse_record(self, record_str):
        """Parsea récord '19-6-0' a dict"""
        parts = record_str.split('-')
        if len(parts) == 3:
            return {
                'wins': int(parts[0]),
                'losses': int(parts[1]),
                'draws': int(parts[2])
            }
        return {'wins': 0, 'losses': 0, 'draws': 0}
