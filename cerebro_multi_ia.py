# -*- coding: utf-8 -*-
"""
CEREBRO MULTI IA - Orquestador para Gemini, Grok y DeepSeek
Permite consultar las 3 IAs simultáneamente y combinar sus análisis
"""

import os
import logging
import streamlit as st
import requests
import json
from typing import Dict, List

logger = logging.getLogger(__name__)

class CerebroMultiIA:
    def __init__(self):
        self.gemini_key = self._get_api_key('GEMINI_API_KEY')
        self.grok_key = self._get_api_key('GROK_API_KEY')
        self.deepseek_key = self._get_api_key('DEEPSEEK_API_KEY')
        
        self.gemini_available = bool(self.gemini_key)
        self.grok_available = bool(self.grok_key)
        self.deepseek_available = bool(self.deepseek_key)
        
        if self.gemini_available:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("✅ Gemini configurado")
            except:
                self.gemini_available = False
        
        if self.deepseek_available:
            self.deepseek_url = "https://api.deepseek.com/v1/chat/completions"
        
        logger.info(f"Multi-IA: Gemini={self.gemini_available}, Grok={self.grok_available}, DeepSeek={self.deepseek_available}")

    def _get_api_key(self, key_name):
        """Obtiene API key desde secrets o .env"""
        try:
            if hasattr(st, 'secrets') and key_name in st.secrets:
                return st.secrets[key_name]
        except:
            pass
        try:
            with open('.env', 'r') as f:
                for linea in f:
                    if key_name in linea:
                        return linea.split('=')[1].strip().strip('"').strip("'")
        except:
            pass
        return os.environ.get(key_name)

    def consultar_gemini(self, prompt):
        """Consulta a Gemini con manejo de errores"""
        if not self.gemini_available:
            return None
        
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error en Gemini: {e}")
            return None

    def consultar_grok(self, prompt):
        """Consulta a Grok (usando xAI API)"""
        if not self.grok_available:
            return None
        
        try:
            # Grok API (xAI)
            url = "https://api.x.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.grok_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "grok-beta",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 300
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=15)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"Error en Grok: {e}")
        return None

    def consultar_deepseek(self, prompt):
        """Consulta a DeepSeek"""
        if not self.deepseek_available:
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.deepseek_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 300
            }
            
            response = requests.post(self.deepseek_url, headers=headers, json=data, timeout=15)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"Error en DeepSeek: {e}")
        return None

    def orquestrar_analisis(self, deporte: str, partido: Dict, analisis_motor: Dict) -> Dict:
        """
        Orquesta el análisis de las 3 IAs:
        - DeepSeek: Valida estructura de datos
        - Grok: Busca noticias/lesiones recientes
        - Gemini: Análisis predictivo final
        """
        # Preparar datos para las IAs
        datos_json = json.dumps({
            'deporte': deporte,
            'partido': partido,
            'analisis': analisis_motor
        }, ensure_ascii=False)
        
        resultado = {
            'deepseek_validacion': None,
            'grok_noticias': None,
            'gemini_prediccion': None,
            'consenso': None
        }
        
        # 1. DeepSeek: Valida estructura y datos
        prompt_deepseek = f"""
Eres un validador de datos. Analiza este JSON y responde SOLO con:
- "VALIDO" si la estructura es correcta
- "INVALIDO: [razón]" si hay problemas

No agregues texto adicional.

JSON:
{datos_json}
"""
        resultado['deepseek_validacion'] = self.consultar_deepseek(prompt_deepseek)
        
        # 2. Grok: Busca noticias/lesiones
        prompt_grok = f"""
Busca información sobre este partido de {deporte}:
Local: {partido.get('home', partido.get('peleador1', 'N/A'))}
Visitante: {partido.get('away', partido.get('peleador2', 'N/A'))}

Responde en 2 líneas máximo sobre:
- Lesiones importantes
- Noticias de última hora
- Factores externos (clima, viajes, etc.)

Si no hay información, responde "Sin noticias relevantes"
"""
        resultado['grok_noticias'] = self.consultar_grok(prompt_grok)
        
        # 3. Gemini: Análisis predictivo
        recomendacion = analisis_motor.get('recomendacion', 'N/A')
        confianza = analisis_motor.get('confianza', 50)
        
        prompt_gemini = f"""
Eres un Sharp Bettor profesional. Analiza este pick:

Deporte: {deporte}
Partido: {partido.get('home', partido.get('peleador1', ''))} vs {partido.get('away', partido.get('peleador2', ''))}
Pick del motor: {recomendacion}
Confianza: {confianza}%

Noticias/contexto: {resultado['grok_noticias'] or 'Sin información adicional'}

Reglas:
- Usa terminología profesional (EV, Variance, Matchup)
- Responde en 2 líneas máximo
- No saludes
- Si el pick tiene valor, menciónalo
"""
        resultado['gemini_prediccion'] = self.consultar_gemini(prompt_gemini)
        
        # 4. Consenso (si todas las IAs coinciden)
        if resultado['deepseek_validacion'] == 'VALIDO' and resultado['gemini_prediccion']:
            resultado['consenso'] = f"""
🎯 ANÁLISIS CONSENSO (Gemini + Grok)

{resultado['gemini_prediccion']}

📰 Contexto: {resultado['grok_noticias'] or 'Sin novedades'}
"""
        
        return resultado

    def generar_prompt_maestro(self, deporte: str, analisis_motor: Dict) -> str:
        """Genera un prompt optimizado según el deporte"""
        base = """
Actúa como un analista profesional de apuestas deportivas.
Usa terminología de Expected Value (EV), Variance y Matchup Analysis.
Responde en máximo 3 líneas. No saludes.
"""
        
        if deporte == "UFC":
            return base + f"""
Evento: {analisis_motor.get('evento', 'N/A')}
Ganador: {analisis_motor.get('ganador', 'N/A')}
Analiza el 'Styles Make Fights'. Considera el alcance y el estilo.
"""
        
        elif deporte == "NBA":
            return base + f"""
Juego: {analisis_motor.get('evento', 'N/A')}
Analiza el Pace of Play y la eficiencia defensiva en el perímetro.
"""
        
        elif deporte == "MLB":
            return base + f"""
Juego: {analisis_motor.get('evento', 'N/A')}
Analiza el ERA del pitcher y los factores del estadio (park factors).
"""
        
        elif deporte == "FÚTBOL":
            return base + f"""
Liga: {analisis_motor.get('liga', 'N/A')}
Partido: {analisis_motor.get('evento', 'N/A')}
Pick: {analisis_motor.get('recomendacion', 'N/A')}
Analiza el xG (Expected Goals) y la posesión efectiva.
"""
        
        return base


# Instancia global
cerebro_multi = CerebroMultiIA()
