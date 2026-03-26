"""
ANALIZADOR UFC MAESTRO - Con análisis real basado en datos de Kaggle
Basado en las sugerencias de Gemini: Ventaja de alcance, KO Rate real, Grappling
"""
import sqlite3

class AnalizadorUFCMaestro:
    def __init__(self, api_key_gemini=None):
        self.db_path = 'data/betting_stats.db'
        self.gemini = None
        if api_key_gemini:
            try:
                from cerebro_gemini_pro import CerebroGemini
                self.gemini = CerebroGemini(api_key_gemini)
            except:
                pass
    
    def obtener_datos_peleador(self, nombre):
        """Obtiene datos REALES del peleador desde SQLite (Kaggle)"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("""
                SELECT nombre, record, altura, peso, alcance, postura, ko_rate, grappling
                FROM peleadores_ufc 
                WHERE nombre LIKE ? OR nombre = ?
                LIMIT 1
            """, (f"%{nombre}%", nombre))
            row = c.fetchone()
            conn.close()
            
            if row:
                return {
                    'nombre': row[0],
                    'record': row[1] if row[1] else '0-0-0',
                    'altura': row[2] if row[2] else 'N/A',
                    'peso': row[3] if row[3] else 'N/A',
                    'alcance': row[4] if row[4] else 'N/A',
                    'postura': row[5] if row[5] else 'Desconocida',
                    'ko_rate': float(row[6]) if row[6] else 0.5,
                    'grappling': float(row[7]) if row[7] else 0.5
                }
            return None
        except Exception as e:
            print(f"Error obteniendo {nombre}: {e}")
            return None
    
    def analizar_combate(self, peleador1, peleador2):
        """Analiza combate con datos REALES"""
        
        # Obtener datos de la base de datos si no vienen completos
        if isinstance(peleador1, dict) and 'ko_rate' not in peleador1:
            p1 = self.obtener_datos_peleador(peleador1.get('nombre', ''))
        else:
            p1 = peleador1
        
        if isinstance(peleador2, dict) and 'ko_rate' not in peleador2:
            p2 = self.obtener_datos_peleador(peleador2.get('nombre', ''))
        else:
            p2 = peleador2
        
        if not p1 or not p2:
            return {
                'ganador': 'N/A',
                'probabilidad': 0,
                'metodo': 'N/A',
                'etiqueta_verde': False,
                'gemini_opinion': 'Datos insuficientes'
            }
        
        # Extraer datos REALES
        alcance1 = self._extraer_numero(p1.get('alcance', '0'))
        alcance2 = self._extraer_numero(p2.get('alcance', '0'))
        ko_rate1 = p1.get('ko_rate', 0.5)
        ko_rate2 = p2.get('ko_rate', 0.5)
        grappling1 = p1.get('grappling', 0.5)
        grappling2 = p2.get('grappling', 0.5)
        
        # VENTAJA DE ALCANCE (lo que Gemini sugirió)
        diff_alcance = alcance1 - alcance2
        
        # AJUSTE DE KO POR GRAPPLING (lo que Gemini sugirió)
        ko_ajustado1 = ko_rate1 * (1 - (grappling2 * 0.3))
        ko_ajustado2 = ko_rate2 * (1 - (grappling1 * 0.3))
        prob_ko = max(ko_ajustado1, ko_ajustado2) * 100
        
        # JERARQUÍA DE DECISIÓN (lo que Gemini sugirió)
        if abs(diff_alcance) >= 5 and prob_ko >= 60:
            ganador = p1.get('nombre') if diff_alcance > 0 else p2.get('nombre')
            probabilidad = 70 + min(20, abs(diff_alcance) * 2)
            metodo = "KO/TKO" if prob_ko > 65 else "Decisión"
            etiqueta_verde = probabilidad >= 75
            
        elif prob_ko >= 70:
            ganador = p1.get('nombre') if ko_ajustado1 > ko_ajustado2 else p2.get('nombre')
            probabilidad = prob_ko
            metodo = "KO/TKO"
            etiqueta_verde = probabilidad >= 75
            
        else:
            ganador = p1.get('nombre') if ko_rate1 > ko_rate2 else p2.get('nombre')
            probabilidad = 55 + (max(ko_rate1, ko_rate2) * 20)
            metodo = "Decisión"
            etiqueta_verde = False
        
        # Gemini para contexto adicional
        gemini_opinion = ""
        if self.gemini:
            try:
                resumen = f"Alcance: {alcance1} vs {alcance2} cm | KO Rate: {ko_rate1*100:.0f}% vs {ko_rate2*100:.0f}%"
                gemini_opinion = self.gemini.analizar_ufc(p1.get('nombre'), p2.get('nombre'), resumen)
            except:
                gemini_opinion = "Gemini no disponible"
        
        return {
            'ganador': ganador,
            'probabilidad': int(probabilidad),
            'metodo': metodo,
            'etiqueta_verde': etiqueta_verde,
            'alcance_p1': alcance1,
            'alcance_p2': alcance2,
            'prob_ko': int(prob_ko),
            'ventaja_clave': f"Alcance: {abs(diff_alcance)} cm" if abs(diff_alcance) > 0 else "Equilibrado",
            'gemini_opinion': gemini_opinion,
            'stats_p1': {
                'ko_rate': int(ko_rate1 * 100),
                'grappling': int(grappling1 * 100),
                'alcance': alcance1
            },
            'stats_p2': {
                'ko_rate': int(ko_rate2 * 100),
                'grappling': int(grappling2 * 100),
                'alcance': alcance2
            }
        }
    
    def _extraer_numero(self, valor):
        """Extrae número de un string como '178 cm'"""
        if isinstance(valor, (int, float)):
            return valor
        if isinstance(valor, str):
            import re
            nums = re.findall(r'\d+', valor)
            return int(nums[0]) if nums else 0
        return 0
