"""
ANALIZADOR UFC PREMIUM - Análisis avanzado de peleas UFC
"""
class AnalizadorUFCPremium:
    def __init__(self):
        pass
    
    def _extraer_numero(self, valor):
        """Extrae número de un string como '178 cm'"""
        if valor is None:
            return 0
        if isinstance(valor, (int, float)):
            return valor
        if isinstance(valor, str):
            import re
            nums = re.findall(r'\d+', valor)
            return int(nums[0]) if nums else 0
        return 0
    
    def analizar(self, p1_data, p2_data, resultado_heur):
        """Analiza pelea UFC con criterios premium"""
        
        p1_nombre = p1_data.get('nombre', 'Peleador 1') if p1_data else 'Peleador 1'
        p2_nombre = p2_data.get('nombre', 'Peleador 2') if p2_data else 'Peleador 2'
        
        # Obtener datos del análisis heurístico
        ganador = resultado_heur.get('ganador', p1_nombre)
        probabilidad = resultado_heur.get('confianza', 55)
        metodo = resultado_heur.get('metodo', 'Decisión')
        etiqueta_verde = resultado_heur.get('etiqueta_verde', False)
        
        # Datos adicionales de peleadores - convertir a números
        alcance1 = self._extraer_numero(p1_data.get('alcance', '0')) if p1_data else 0
        alcance2 = self._extraer_numero(p2_data.get('alcance', '0')) if p2_data else 0
        ko1 = p1_data.get('ko_rate', 0.5) if p1_data else 0.5
        ko2 = p2_data.get('ko_rate', 0.5) if p2_data else 0.5
        
        # Análisis premium: ajustar confianza
        diff_alcance = alcance1 - alcance2
        if abs(diff_alcance) > 5:
            if (diff_alcance > 0 and ganador == p1_nombre) or (diff_alcance < 0 and ganador == p2_nombre):
                probabilidad = min(95, probabilidad + 10)
                etiqueta_verde = probabilidad >= 75
        
        # Análisis de KO
        if metodo == "KO/TKO" and max(ko1, ko2) > 0.6:
            probabilidad = min(95, probabilidad + 5)
        
        return {
            'ganador': ganador,
            'probabilidad': probabilidad,
            'metodo': metodo,
            'etiqueta_verde': etiqueta_verde,
            'analisis': f"Ventaja de {'alcance' if abs(diff_alcance) > 5 else 'KO'} detectada",
            'confianza': probabilidad,
            'diff_alcance': diff_alcance
        }
