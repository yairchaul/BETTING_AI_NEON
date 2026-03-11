"""
SISTEMA MULTI-AGENTE - Claude + GPT debaten picks deportivos
"""
import os
import json
import requests
from typing import List, Dict, Any
from datetime import datetime

# ============================================
# CONFIGURACIÓN DE APIS
# ============================================
class AIConfig:
    """Configuración para diferentes modelos de IA"""
    
    CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
    
    @classmethod
    def estan_configuradas(cls):
        """Verifica si hay al menos una API configurada"""
        return bool(cls.CLAUDE_API_KEY or cls.OPENAI_API_KEY)

# ============================================
# AGENTE BASE
# ============================================
class AgenteIA:
    """Clase base para agentes de IA"""
    
    def __init__(self, nombre: str, modelo: str):
        self.nombre = nombre
        self.modelo = modelo
        self.historial = []
    
    def analizar_pick(self, pick: Dict, contexto: Dict) -> Dict:
        """Analiza un pick y da su opinión"""
        raise NotImplementedError

# ============================================
# AGENTE CLAUDE (Anthropic)
# ============================================
class AgenteClaude(AgenteIA):
    """Agente usando Claude de Anthropic"""
    
    def __init__(self):
        super().__init__("Claude 3.5 Sonnet", "claude-3-5-sonnet-20241022")
        self.api_key = AIConfig.CLAUDE_API_KEY
    
    def analizar_pick(self, pick: Dict, contexto: Dict) -> Dict:
        """Claude analiza un pick específico"""
        
        if not self.api_key:
            return self._analisis_fallback(pick)
        
        prompt = f"""
        Como experto en apuestas deportivas con 20 años de experiencia, analiza este pick:
        
        PARTIDO: {pick.get('partido', 'Desconocido')}
        LIGA: {pick.get('liga', 'Desconocida')}
        PICK: {pick.get('desc', 'Desconocido')}
        PROBABILIDAD CALCULADA: {pick.get('prob', 0)*100:.1f}%
        CUOTA: {pick.get('cuota', 0):.2f}
        VALUE: {(pick.get('value', 0)*100):.1f}%
        NIVEL DE REGLA: {pick.get('nivel', 0)}
        
        CONTEXTO ADICIONAL:
        - Goles esperados local: {contexto.get('gf_local', 'N/A')}
        - Goles esperados visitante: {contexto.get('gf_visit', 'N/A')}
        
        Por favor, responde en formato JSON con:
        1. opinion: "FAVORABLE" o "DESFAVORABLE" o "NEUTRAL"
        2. confianza: número del 0 al 100
        3. justificacion: breve explicación (máx 2 líneas)
        4. sugerencia: "APOSTAR" o "EVITAR" o "ANALIZAR_MAS"
        """
        
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            data = {
                "model": self.modelo,
                "max_tokens": 300,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
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
                            'opinion': analisis.get('opinion', 'NEUTRAL'),
                            'confianza': analisis.get('confianza', 50),
                            'justificacion': analisis.get('justificacion', ''),
                            'sugerencia': analisis.get('sugerencia', 'ANALIZAR_MAS')
                        }
                except:
                    pass
            
            return self._analisis_fallback(pick)
            
        except Exception as e:
            print(f"Error en Claude: {e}")
            return self._analisis_fallback(pick)
    
    def _analisis_fallback(self, pick):
        """Análisis de respaldo cuando la API no responde"""
        if pick.get('value', 0) > 0.10:
            return {
                'agente': self.nombre,
                'pick_desc': pick.get('desc', ''),
                'opinion': 'FAVORABLE',
                'confianza': 85,
                'justificacion': 'Value muy alto (>10%)',
                'sugerencia': 'APOSTAR'
            }
        elif pick.get('nivel', 7) <= 3 and pick.get('prob', 0) > 0.70:
            return {
                'agente': self.nombre,
                'pick_desc': pick.get('desc', ''),
                'opinion': 'FAVORABLE',
                'confianza': 75,
                'justificacion': 'Regla temprana con alta probabilidad',
                'sugerencia': 'APOSTAR'
            }
        else:
            return {
                'agente': self.nombre,
                'pick_desc': pick.get('desc', ''),
                'opinion': 'NEUTRAL',
                'confianza': 50,
                'justificacion': 'Valor moderado, analizar más',
                'sugerencia': 'ANALIZAR_MAS'
            }

# ============================================
# AGENTE GPT (OpenAI)
# ============================================
class AgenteGPT(AgenteIA):
    """Agente usando GPT de OpenAI"""
    
    def __init__(self):
        super().__init__("GPT-4 Turbo", "gpt-4-turbo-preview")
        self.api_key = AIConfig.OPENAI_API_KEY
    
    def analizar_pick(self, pick: Dict, contexto: Dict) -> Dict:
        """GPT analiza un pick específico"""
        
        if not self.api_key:
            return self._analisis_fallback(pick)
        
        prompt = f"""
        Eres un analista de apuestas deportivas profesional. Analiza este pick:
        
        Partido: {pick.get('partido', 'Desconocido')}
        Liga: {pick.get('liga', 'Desconocida')}
        Pick: {pick.get('desc', 'Desconocido')}
        Probabilidad: {pick.get('prob', 0)*100:.1f}%
        Cuota: {pick.get('cuota', 0):.2f}
        Value: {(pick.get('value', 0)*100):.1f}%
        
        Responde SOLO con un JSON:
        {{"opinion": "FAVORABLE/DESFAVORABLE/NEUTRAL", "confianza": 0-100, "razon": "breve razón"}}
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
                "max_tokens": 150
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
                        'opinion': analisis.get('opinion', 'NEUTRAL'),
                        'confianza': analisis.get('confianza', 50),
                        'justificacion': analisis.get('razon', ''),
                        'sugerencia': 'APOSTAR' if analisis.get('opinion') == 'FAVORABLE' else 'EVITAR'
                    }
                except:
                    pass
            
            return self._analisis_fallback(pick)
            
        except Exception as e:
            print(f"Error en GPT: {e}")
            return self._analisis_fallback(pick)
    
    def _analisis_fallback(self, pick):
        """Análisis de respaldo para GPT"""
        if pick.get('value', 0) > 0.15:
            return {
                'agente': self.nombre,
                'pick_desc': pick.get('desc', ''),
                'opinion': 'FAVORABLE',
                'confianza': 80,
                'justificacion': 'Value excepcional',
                'sugerencia': 'APOSTAR'
            }
        elif pick.get('prob', 0) > 0.80:
            return {
                'agente': self.nombre,
                'pick_desc': pick.get('desc', ''),
                'opinion': 'FAVORABLE',
                'confianza': 70,
                'justificacion': 'Probabilidad muy alta',
                'sugerencia': 'APOSTAR'
            }
        else:
            return {
                'agente': self.nombre,
                'pick_desc': pick.get('desc', ''),
                'opinion': 'NEUTRAL',
                'confianza': 40,
                'justificacion': 'Sin suficiente convicción',
                'sugerencia': 'ANALIZAR_MAS'
            }

# ============================================
# SISTEMA DE DEBATE MULTI-AGENTE
# ============================================
class MultiAgentDebate:
    """Sistema donde múltiples IAs debaten picks"""
    
    def __init__(self):
        self.agentes = []
        
        if AIConfig.CLAUDE_API_KEY:
            self.agentes.append(AgenteClaude())
        
        if AIConfig.OPENAI_API_KEY:
            self.agentes.append(AgenteGPT())
        
        if not self.agentes:
            self.agentes = [AgenteClaude(), AgenteGPT()]
    
    def debatir_pick(self, pick: Dict, contexto: Dict) -> Dict:
        """Todos los agentes analizan un pick y se llega a consenso"""
        opiniones = []
        
        for agente in self.agentes:
            opinion = agente.analizar_pick(pick, contexto)
            opiniones.append(opinion)
        
        votos_favor = sum(1 for o in opiniones if o['opinion'] == 'FAVORABLE')
        votos_contra = sum(1 for o in opiniones if o['opinion'] == 'DESFAVORABLE')
        total_agentes = len(self.agentes)
        
        confianza_promedio = sum(o.get('confianza', 0) for o in opiniones) / total_agentes
        
        if votos_favor > total_agentes / 2:
            decision = 'APOSTAR'
            consenso = 'FAVORABLE'
        elif votos_contra > total_agentes / 2:
            decision = 'EVITAR'
            consenso = 'DESFAVORABLE'
        else:
            decision = 'ANALIZAR_MAS'
            consenso = 'NEUTRAL'
        
        return {
            'pick': pick,
            'consenso': consenso,
            'decision': decision,
            'confianza': confianza_promedio,
            'votos_favor': votos_favor,
            'votos_contra': votos_contra,
            'total_agentes': total_agentes,
            'opiniones': opiniones,
            'justificacion': self._generar_justificacion(opiniones)
        }
    
    def _generar_justificacion(self, opiniones):
        razones = [o.get('justificacion', '') for o in opiniones if o.get('justificacion')]
        if razones:
            return " | ".join(razones[:2])
        return "Debate completado sin consenso claro"
    
    def obtener_top_consenso(self, picks: List[Dict], top_n: int = 5) -> List[Dict]:
        """Obtiene los mejores picks por consenso entre agentes"""
        resultados = []
        
        for pick in picks:
            contexto = {
                'gf_local': pick.get('gf_local', 0),
                'gf_visit': pick.get('gf_visit', 0)
            }
            
            resultado = self.debatir_pick(pick, contexto)
            
            if resultado['consenso'] == 'FAVORABLE':
                score = resultado['confianza'] / 100
            elif resultado['consenso'] == 'NEUTRAL':
                score = 0.3
            else:
                score = 0
            
            resultados.append({
                'pick': pick,
                'score_consenso': score,
                'decision': resultado['decision'],
                'confianza': resultado['confianza'],
                'justificacion': resultado['justificacion'],
                'votos_favor': resultado['votos_favor'],
                'votos_contra': resultado['votos_contra']
            })
        
        return sorted(resultados, key=lambda x: x['score_consenso'], reverse=True)[:top_n]
