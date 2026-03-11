"""
SISTEMA MULTI-AGENTE CON LAS 7 REGLAS
Los agentes debaten usando la jerarquía de reglas como criterio
"""
import os
import json
import requests
from typing import List, Dict, Any
from datetime import datetime

# ============================================
# LAS 7 REGLAS (para referencia de los agentes)
# ============================================
REGLAS_FUTBOL = """
JERARQUÍA DE 7 REGLAS (orden de prioridad):

REGLA 1: Over 1.5 Primer Tiempo > 60%
- Prioridad máxima - Goles tempranos
- Ejemplo: Over 1.5 1T con 65% de probabilidad

REGLA 2: Over 3.5 + Favorito claro
- Over 3.5 > 60% Y favorito >55%
- Genera 2 picks: victoria favorito + Over 3.5
- Ejemplo: Real Madrid gana (60%) + Over 3.5 (62%)

REGLA 3: BTTS (Both Teams To Score) > 60%
- Ambos equipos anotan
- Ejemplo: BTTS Sí con 65% de probabilidad

REGLA 4: Partido equilibrado → Mejor over cercano a 55%
- Ningún equipo supera 55%
- Se elige el over MÁS CERCANO a 55% (no el de mayor prob)
- Ejemplo: Over 2.5 con 56% (cercano a 55%)

REGLA 5: Favorito local + Mejor over
- Local >50% Y Visitante <40%
- Genera 2 picks: victoria local + mejor over
- Ejemplo: Liverpool gana (58%) + Over 2.5 (61%)

REGLA 6: Favorito visitante + Mejor over
- Visitante >50% Y Local <40%
- Genera 2 picks: victoria visitante + mejor over
- Ejemplo: Manchester City gana (59%) + Over 2.5 (60%)

REGLA 7: Default → Mejor over
- Si ninguna regla aplica, se elige el over con mayor probabilidad
"""

# ============================================
# CONFIGURACIÓN DE APIS
# ============================================
class AIConfig:
    CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# ============================================
# AGENTE BASE
# ============================================
class AgenteIA:
    def __init__(self, nombre: str, modelo: str):
        self.nombre = nombre
        self.modelo = modelo
    
    def analizar_con_reglas(self, pick: Dict, contexto: Dict) -> Dict:
        """Analiza un pick considerando las 7 reglas"""
        raise NotImplementedError

# ============================================
# AGENTE CLAUDE (Analiza con las 7 reglas)
# ============================================
class AgenteClaudeReglas(AgenteIA):
    def __init__(self):
        super().__init__("Claude 3.5 Sonnet (Experto en reglas)", "claude-3-5-sonnet-20241022")
        self.api_key = AIConfig.CLAUDE_API_KEY
    
    def analizar_con_reglas(self, pick: Dict, contexto: Dict) -> Dict:
        """Claude analiza aplicando las 7 reglas"""
        
        prompt = f"""
        Eres un experto en apuestas deportivas especializado en las 7 REGLAS JERÁRQUICAS.
        
        {REGLAS_FUTBOL}
        
        Analiza este pick según las reglas:
        
        PARTIDO: {pick.get('partido', 'Desconocido')}
        LIGA: {pick.get('liga', 'Desconocida')}
        PICK: {pick.get('desc', 'Desconocido')}
        
        PROBABILIDADES CALCULADAS:
        - Over 1.5: {contexto.get('over_15', 0)*100:.1f}%
        - Over 2.5: {contexto.get('over_25', 0)*100:.1f}%
        - Over 3.5: {contexto.get('over_35', 0)*100:.1f}%
        - BTTS: {contexto.get('btts', 0)*100:.1f}%
        - Local gana: {contexto.get('prob_local', 0)*100:.1f}%
        - Visitante gana: {contexto.get('prob_visit', 0)*100:.1f}%
        - Empate: {contexto.get('prob_empate', 0)*100:.1f}%
        
        GOLES ESPERADOS:
        - Local: {contexto.get('gf_local', 0):.2f}
        - Visitante: {contexto.get('gf_visit', 0):.2f}
        
        VALUE DEL PICK: {pick.get('value', 0)*100:.1f}%
        
        Basado en las 7 reglas, responde en formato JSON:
        1. regla_aplicable: número de la regla que aplicaría (1-7)
        2. justificacion_regla: por qué aplica esa regla
        3. opinion: "FAVORABLE" o "DESFAVORABLE" o "NEUTRAL"
        4. confianza: 0-100
        5. sugerencia: "APOSTAR" o "EVITAR" o "ANALIZAR_MAS"
        6. explicacion: cómo se alinea con la jerarquía de reglas
        """
        
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            data = {
                "model": self.modelo,
                "max_tokens": 500,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            response = requests.post(AIConfig.CLAUDE_API_URL, headers=headers, json=data, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                contenido = result.get('content', [{}])[0].get('text', '{}')
                
                try:
                    import re
                    json_match = re.search(r'\{.*\}', contenido, re.DOTALL)
                    if json_match:
                        analisis = json.loads(json_match.group())
                        return {
                            'agente': self.nombre,
                            'pick_desc': pick.get('desc', ''),
                            'regla_aplicable': analisis.get('regla_aplicable', 0),
                            'justificacion_regla': analisis.get('justificacion_regla', ''),
                            'opinion': analisis.get('opinion', 'NEUTRAL'),
                            'confianza': analisis.get('confianza', 50),
                            'sugerencia': analisis.get('sugerencia', 'ANALIZAR_MAS'),
                            'explicacion': analisis.get('explicacion', '')
                        }
                except:
                    pass
            
            return self._analisis_fallback(pick, contexto)
            
        except Exception as e:
            print(f"Error en Claude: {e}")
            return self._analisis_fallback(pick, contexto)
    
    def _analisis_fallback(self, pick, contexto):
        """Análisis basado en reglas cuando la API no responde"""
        # Verificar qué regla aplicaría
        regla = 7  # Default
        justificacion = "Regla 7 (Default)"
        
        if contexto.get('over_15_1t', 0) > 0.60:
            regla = 1
            justificacion = "Regla 1: Over 1.5 1T > 60%"
        elif contexto.get('over_35', 0) > 0.60 and (contexto.get('prob_local', 0) > 0.55 or contexto.get('prob_visit', 0) > 0.55):
            regla = 2
            justificacion = "Regla 2: Over 3.5 + favorito claro"
        elif contexto.get('btts', 0) > 0.60:
            regla = 3
            justificacion = "Regla 3: BTTS > 60%"
        
        if pick.get('value', 0) > 0.10:
            return {
                'agente': self.nombre,
                'pick_desc': pick.get('desc', ''),
                'regla_aplicable': regla,
                'justificacion_regla': justificacion,
                'opinion': 'FAVORABLE',
                'confianza': 85,
                'sugerencia': 'APOSTAR',
                'explicacion': f'{justificacion} y value alto ({pick["value"]*100:.1f}%)'
            }
        else:
            return {
                'agente': self.nombre,
                'pick_desc': pick.get('desc', ''),
                'regla_aplicable': regla,
                'justificacion_regla': justificacion,
                'opinion': 'NEUTRAL',
                'confianza': 50,
                'sugerencia': 'ANALIZAR_MAS',
                'explicacion': f'{justificacion} pero value bajo'
            }

# ============================================
# AGENTE GPT (Analiza con las 7 reglas)
# ============================================
class AgenteGPTReglas(AgenteIA):
    def __init__(self):
        super().__init__("GPT-4 Turbo (Analista de reglas)", "gpt-4-turbo-preview")
        self.api_key = AIConfig.OPENAI_API_KEY
    
    def analizar_con_reglas(self, pick: Dict, contexto: Dict) -> Dict:
        """GPT analiza aplicando las 7 reglas"""
        
        prompt = f"""
        Eres un analista de apuestas experto en las 7 reglas jerárquicas.
        
        {REGLAS_FUTBOL}
        
        Datos del pick:
        Partido: {pick.get('partido')}
        Pick: {pick.get('desc')}
        Probabilidad: {pick.get('prob', 0)*100:.1f}%
        Value: {pick.get('value', 0)*100:.1f}%
        
        Contexto del partido:
        - Over 1.5: {contexto.get('over_15', 0)*100:.1f}%
        - Over 2.5: {contexto.get('over_25', 0)*100:.1f}%
        - Over 3.5: {contexto.get('over_35', 0)*100:.1f}%
        - BTTS: {contexto.get('btts', 0)*100:.1f}%
        - Prob Local: {contexto.get('prob_local', 0)*100:.1f}%
        - Prob Visit: {contexto.get('prob_visit', 0)*100:.1f}%
        
        Responde SOLO con JSON:
        {{
            "regla_aplicable": 1-7,
            "justificacion": "breve por qué aplica esa regla",
            "decision": "APOSTAR/EVITAR/ANALIZAR",
            "confianza": 0-100,
            "explicacion": "cómo se alinea con la jerarquía"
        }}
        """
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.modelo,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 300
            }
            
            response = requests.post(AIConfig.OPENAI_API_URL, headers=headers, json=data, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                contenido = result.get('choices', [{}])[0].get('message', {}).get('content', '{}')
                
                try:
                    analisis = json.loads(contenido)
                    return {
                        'agente': self.nombre,
                        'pick_desc': pick.get('desc', ''),
                        'regla_aplicable': analisis.get('regla_aplicable', 0),
                        'justificacion_regla': analisis.get('justificacion', ''),
                        'opinion': 'FAVORABLE' if analisis.get('decision') == 'APOSTAR' else 'DESFAVORABLE' if analisis.get('decision') == 'EVITAR' else 'NEUTRAL',
                        'confianza': analisis.get('confianza', 50),
                        'sugerencia': analisis.get('decision', 'ANALIZAR_MAS'),
                        'explicacion': analisis.get('explicacion', '')
                    }
                except:
                    pass
            
            return self._analisis_fallback(pick, contexto)
            
        except Exception as e:
            return self._analisis_fallback(pick, contexto)
    
    def _analisis_fallback(self, pick, contexto):
        """Fallback basado en reglas"""
        # Determinar regla aplicable
        regla = 7
        if contexto.get('over_35', 0) > 0.60:
            regla = 2
        elif contexto.get('btts', 0) > 0.60:
            regla = 3
        
        return {
            'agente': self.nombre,
            'pick_desc': pick.get('desc', ''),
            'regla_aplicable': regla,
            'justificacion_regla': f'Regla {regla} por contexto',
            'opinion': 'FAVORABLE' if pick.get('value', 0) > 0.05 else 'NEUTRAL',
            'confianza': 70 if pick.get('value', 0) > 0.05 else 40,
            'sugerencia': 'APOSTAR' if pick.get('value', 0) > 0.05 else 'ANALIZAR_MAS',
            'explicacion': f'Regla {regla} con value {pick.get("value",0)*100:.1f}%'
        }

# ============================================
# SISTEMA DE DEBATE CON REGLAS
# ============================================
class DebateConReglas:
    """Sistema donde los agentes debaten usando las 7 reglas"""
    
    def __init__(self):
        self.agentes = []
        
        if AIConfig.CLAUDE_API_KEY:
            self.agentes.append(AgenteClaudeReglas())
        if AIConfig.OPENAI_API_KEY:
            self.agentes.append(AgenteGPTReglas())
        
        if not self.agentes:
            self.agentes = [AgenteClaudeReglas(), AgenteGPTReglas()]
    
    def debatir_pick(self, pick: Dict, contexto: Dict) -> Dict:
        """Debate sobre qué regla aplicar"""
        opiniones = []
        
        for agente in self.agentes:
            opinion = agente.analizar_con_reglas(pick, contexto)
            opiniones.append(opinion)
        
        # Análisis de reglas
        reglas_aplicadas = [o.get('regla_aplicable', 7) for o in opiniones]
        regla_mas_comun = max(set(reglas_aplicadas), key=reglas_aplicadas.count)
        
        # Votación
        votos_favor = sum(1 for o in opiniones if o['opinion'] == 'FAVORABLE')
        votos_contra = sum(1 for o in opiniones if o['opinion'] == 'DESFAVORABLE')
        total = len(self.agentes)
        
        confianza_promedio = sum(o.get('confianza', 0) for o in opiniones) / total
        
        # Decisión basada en reglas + votos
        if regla_mas_comun <= 3 and votos_favor > total/2:
            decision = 'APOSTAR'
            consenso = 'FAVORABLE'
        elif regla_mas_comun <= 4 and votos_favor > 0:
            decision = 'ANALIZAR_MAS'
            consenso = 'NEUTRAL'
        else:
            decision = 'EVITAR'
            consenso = 'DESFAVORABLE'
        
        return {
            'pick': pick,
            'consenso': consenso,
            'decision': decision,
            'confianza': confianza_promedio,
            'regla_consenso': regla_mas_comun,
            'votos_favor': votos_favor,
            'votos_contra': votos_contra,
            'opiniones': opiniones,
            'justificacion': self._generar_justificacion(opiniones, regla_mas_comun)
        }
    
    def _generar_justificacion(self, opiniones, regla):
        razones = [o.get('justificacion_regla', '') for o in opiniones if o.get('justificacion_regla')]
        return f"Regla {regla} seleccionada: {' | '.join(razones[:2])}"
    
    def obtener_mejores_por_regla(self, picks: List[Dict], top_n: int = 5) -> List[Dict]:
        """Obtiene los mejores picks según el consenso de reglas"""
        resultados = []
        
        for pick in picks:
            contexto = {
                'over_15': pick.get('over_15', 0.65),
                'over_25': pick.get('over_25', 0.45),
                'over_35': pick.get('over_35', 0.30),
                'btts': pick.get('btts', 0.55),
                'prob_local': pick.get('prob_local', 0.4),
                'prob_visit': pick.get('prob_visit', 0.3),
                'prob_empate': pick.get('prob_empate', 0.3),
                'gf_local': pick.get('gf_local', 1.5),
                'gf_visit': pick.get('gf_visit', 1.3)
            }
            
            resultado = self.debatir_pick(pick, contexto)
            
            # Score basado en regla (más temprana = mejor) + value
            score = (7 - resultado['regla_consenso'] + 1) * 0.1 + pick.get('value', 0)
            
            resultados.append({
                'pick': pick,
                'score': score,
                'regla': resultado['regla_consenso'],
                'decision': resultado['decision'],
                'confianza': resultado['confianza'],
                'justificacion': resultado['justificacion']
            })
        
        return sorted(resultados, key=lambda x: x['score'], reverse=True)[:top_n]

# ============================================
# PRUEBA RÁPIDA
# ============================================
def probar_debate_con_reglas():
    print("="*70)
    print("🤖 DEBATE MULTI-AGENTE CON LAS 7 REGLAS")
    print("="*70)
    
    # Picks de prueba con contexto
    picks_prueba = [
        {
            'partido': 'Real Madrid vs Manchester City',
            'liga': 'UCL',
            'desc': 'Over 2.5 goles',
            'prob': 0.72,
            'value': 0.33,
            'over_15': 0.85,
            'over_25': 0.72,
            'over_35': 0.58,
            'btts': 0.68,
            'prob_local': 0.48,
            'prob_visit': 0.52,
            'gf_local': 2.4,
            'gf_visit': 2.1
        },
        {
            'partido': 'Bayern Munich vs Atalanta',
            'liga': 'UCL',
            'desc': 'Bayern gana',
            'prob': 0.75,
            'value': 0.01,
            'over_15': 0.70,
            'over_25': 0.45,
            'over_35': 0.25,
            'btts': 0.50,
            'prob_local': 0.68,
            'prob_visit': 0.32,
            'gf_local': 2.8,
            'gf_visit': 1.8
        }
    ]
    
    debate = DebateConReglas()
    
    for pick in picks_prueba:
        print(f"\n🎯 ANALIZANDO: {pick['partido']} - {pick['desc']}")
        print(f"   Value: {pick['value']*100:.1f}%")
        
        resultado = debate.debatir_pick(pick, pick)
        
        print(f"\n   📢 RESULTADO DEL DEBATE:")
        print(f"      Regla consenso: {resultado['regla_consenso']}")
        print(f"      Decisión: {resultado['decision']}")
        print(f"      Confianza: {resultado['confianza']:.1f}%")
        print(f"      Votos: {resultado['votos_favor']} a favor, {resultado['votos_contra']} en contra")
        print(f"      Justificación: {resultado['justificacion']}")
        
        for o in resultado['opiniones']:
            emoji = "👍" if o['opinion'] == 'FAVORABLE' else "👎" if o['opinion'] == 'DESFAVORABLE' else "🤷"
            print(f"        {emoji} {o['agente']}: Regla {o['regla_aplicable']} - {o['justificacion_regla'][:50]}...")
        
        print("-" * 70)

if __name__ == "__main__":
    probar_debate_con_reglas()
