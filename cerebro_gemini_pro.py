# -*- coding: utf-8 -*-
"""
CEREBRO GEMINI PRO - Decisor Final Inteligente (Versión Optimizada para Betting AI NEON)
"""

import os
import logging
import streamlit as st
import google.generativeai as genai
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CerebroGeminiPro:
    def __init__(self, api_key=None, modelo="gemini-2.5-flash"):
        # Prioridad de API Key
        if api_key:
            self.api_key = api_key
        elif hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
            self.api_key = st.secrets['GEMINI_API_KEY']
        else:
            self.api_key = os.environ.get("GEMINI_API_KEY")

        if not self.api_key:
            logger.warning("❌ No se encontró API key de Gemini")
            self.model = None
            return

        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name=modelo,
                generation_config={
                    "temperature": 0.25,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 400,
                }
            )
            logger.info(f"✅ Gemini Pro conectado correctamente con modelo: {modelo}")
        except Exception as e:
            logger.error(f"Error al configurar Gemini: {e}")
            self.model = None

    def orquestrar_decision_final(self, deporte: str, partido: Dict, analisis_heuristico: Dict) -> str:
        """Decisor final que combina motor matemático + razonamiento avanzado de Gemini"""
        if not self.model:
            return "❌ Gemini no disponible - confiando solo en análisis matemático"

        # Extraer datos del partido
        if deporte.upper() == "UFC":
            local = partido.get('peleador1', {}).get('nombre', 'Desconocido')
            visitante = partido.get('peleador2', {}).get('nombre', 'Desconocido')
        else:
            local = partido.get('home', partido.get('local', 'Desconocido'))
            visitante = partido.get('away', partido.get('visitante', 'Desconocido'))

        # Datos clave del análisis matemático
        recomendacion = analisis_heuristico.get('recomendacion', 'N/A')
        confianza_math = analisis_heuristico.get('confianza', 0)
        total_proyectado = analisis_heuristico.get('total_proyectado', 0)
        edge = analisis_heuristico.get('edge', analisis_heuristico.get('ev_mejor', 0))
        prob_math = analisis_heuristico.get('probabilidad', confianza_math)

        prompt = f"""
Eres un analista profesional de apuestas deportivas con más de 15 años de experiencia. Eres conservador y solo recomiendas cuando hay valor real.

**Deporte:** {deporte.upper()}
**Partido:** {local} vs {visitante}

**Análisis Matemático (Motor v20):**
- Recomendación: {recomendacion}
- Confianza matemática: {confianza_math}%
- Probabilidad estimada: {prob_math}%
- Total proyectado: {total_proyectado}
- Edge calculado: {edge:.1f}%

**Cuotas disponibles:** {partido.get('odds', 'No disponibles')}

Tu tarea:
1. Evalúa si el análisis matemático tiene sentido real.
2. Considera factores cualitativos importantes (forma reciente, lesiones, motivación, historial H2H, descanso, etc.).
3. Decide si apoyas la recomendación del motor o sugieres algo diferente.
4. Sé honesto: si no hay valor claro, dilo.

Responde **EXCLUSIVAMENTE** con este formato exacto (no agregues texto extra):

MEJOR APUESTA FINAL: [OVER/UNDER/ML/SPREAD/BTTS/GANA LOCAL/GANA VISITANTE/NO RECOMENDAR]
PROBABILIDAD ESTIMADA: XX%
RAZÓN PRINCIPAL: [máximo una línea clara y concreta]
RIESGO: [Bajo / Medio / Alto]
CONFIANZA IA: [Alta / Media / Baja]
"""

        try:
            response = self.model.generate_content(prompt)
            texto = response.text.strip()

            # Fallback seguro si Gemini no sigue el formato
            if "MEJOR APUESTA FINAL" not in texto or len(texto) < 30:
                return f"""MEJOR APUESTA FINAL: {recomendacion}
PROBABILIDAD ESTIMADA: {confianza_math}%
RAZÓN PRINCIPAL: Análisis matemático sólido del motor v20
RIESGO: Medio
CONFIANZA IA: Media"""

            return texto

        except Exception as e:
            logger.error(f"Error en Gemini: {e}")
            return f"""MEJOR APUESTA FINAL: {recomendacion}
PROBABILIDAD ESTIMADA: {confianza_math}%
RAZÓN PRINCIPAL: Error de conexión con Gemini - confiando en motor matemático
RIESGO: Medio
CONFIANZA IA: Media"""

    def analizar_con_decision(self, partido, analisis_heuristico):
        """Método de compatibilidad con tu código anterior"""
        return self.orquestrar_decision_final("NBA", partido, analisis_heuristico)

    def generar_proyeccion(self, prompt: str):
        """Genera proyección cuando faltan datos"""
        if not self.model:
            return "Gemini no disponible"
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generando proyección: {e}")
            return None


def get_gemini(api_key=None):
    """Helper para mantener compatibilidad"""
    return CerebroGeminiPro(api_key)
