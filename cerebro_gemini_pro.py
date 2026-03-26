# -*- coding: utf-8 -*-
"""
CEREBRO GEMINI PRO - Versión FINAL y estable (marzo 2026)
Compatible con tu test_gemini_simple.py
Usa gemini-2.5-flash (el modelo que sí funciona)
"""

import os
import logging

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("⚠️ Ejecuta: pip install google-genai --upgrade")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CerebroGemini:
    """Cliente Gemini 2026 - estable y simple"""

    def __init__(self, api_key=None, modelo=None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model_name = modelo or "gemini-2.5-flash"   # Forzamos el modelo bueno por defecto
        
        if not self.api_key:
            logger.error("❌ No se encontró GEMINI_API_KEY en .env")
            self.client = None
            return

        if not GENAI_AVAILABLE:
            logger.error("❌ google-genai no instalado")
            self.client = None
            return

        try:
            self.client = genai.Client(api_key=self.api_key)
            logger.info(f"✅ Gemini inicializado con modelo: {self.model_name}")
        except Exception as e:
            logger.error(f"Error al crear cliente Gemini: {e}")
            self.client = None

    def _generar(self, prompt):
        """Método interno para generar contenido"""
        if not self.client:
            return None, "Gemini no disponible"

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip(), None
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"Error Gemini ({self.model_name}): {error_msg[:200]}...")
            return None, error_msg

    def orquestrar_decision_final(self, deporte, partido, analisis_heuristico):
        """Decisor final - Gemini elige la mejor apuesta"""
        if not self.client:
            return "❌ Gemini no disponible - usando análisis matemático"

        local = partido.get('local', '')
        visitante = partido.get('visitante', '')
        rec = analisis_heuristico.get('recomendacion', 'N/A')
        conf = analisis_heuristico.get('confianza', 0)
        total = analisis_heuristico.get('total_proyectado', 0)

        prompt = f"""
Eres el decisor final de BETTING AI NEON.
Deporte: {deporte.upper()}
Partido: {local} vs {visitante}

Análisis matemático: {rec} ({conf}% confianza) | Total proyectado: {total}

Elige la MEJOR APUESTA FINAL según la jerarquía del usuario.
Responde **exactamente** con este formato:

MEJOR APUESTA FINAL: [ej: Over 8.5 / Gana Pittsburgh Pirates / BTTS / Handicap]
PROBABILIDAD: XX%
RAZON: [explicación corta y clara en español]
RIESGO: [Bajo / Medio / Alto]
CONFIANZA IA: [Alta / Media / Baja]
"""

        resultado, error = self._generar(prompt)
        return resultado if resultado else f"Error Gemini: {error}. Usa el pick matemático: {rec}"

    def generar_proyeccion(self, prompt):
        """Genera proyección cuando faltan datos históricos"""
        if not self.client:
            return "9.0"
        resultado, _ = self._generar(prompt)
        return resultado or "9.0"

    # Métodos de compatibilidad (para no romper otros archivos)
    def analizar_contexto_nba(self, local, visitante, stats, contexto=""):
        prompt = f"Partido NBA: {local} vs {visitante}\nDatos: {stats}\n{contexto}"
        resultado, _ = self._generar(prompt)
        return resultado or "Error en Gemini"

    def analizar_ufc(self, peleador1, peleador2, datos):
        prompt = f"Combate UFC: {peleador1} vs {peleador2}\n{datos}"
        resultado, _ = self._generar(prompt)
        return resultado or "Error en Gemini"

    def analizar_futbol(self, local, visitante, stats_local, stats_visit):
        prompt = f"Partido fútbol: {local} vs {visitante}\nLocal: {stats_local}\nVisitante: {stats_visit}"
        resultado, _ = self._generar(prompt)
        return resultado or "Error en Gemini"

def get_gemini(api_key=None):
    return CerebroGemini(api_key)
