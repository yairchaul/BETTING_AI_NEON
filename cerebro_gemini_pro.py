# -*- coding: utf-8 -*-
"""
CEREBRO GEMINI PRO - Decisor Final Inteligente (Versión Optimizada)
"""

import os
import logging
import streamlit as st
import google.generativeai as genai
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CerebroGeminiPro:
    def __init__(self, api_key=None, modelo="gemini-1.5-flash"):
        if api_key:
            self.api_key = api_key
        elif hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
            self.api_key = st.secrets['GEMINI_API_KEY']
        else:
            self.api_key = os.environ.get("GEMINI_API_KEY")

        if not self.api_key:
            logger.warning("❌ No hay API key de Gemini")
            self.model = None
            return

        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name=modelo,
                generation_config={"temperature": 0.25, "max_output_tokens": 400}
            )
            logger.info(f"✅ Gemini Pro conectado ({modelo})")
        except Exception as e:
            logger.error(f"Error Gemini: {e}")
            self.model = None

    def orquestrar_decision_final(self, deporte: str, partido: Dict, analisis: Dict) -> str:
        """Decisor final inteligente con análisis de valor real"""
        if not self.model:
            return "❌ Gemini no disponible - usando solo análisis matemático"

        # Extraer nombres según deporte
        if deporte.upper() == "UFC":
            local = partido.get('peleador1', {}).get('nombre', partido.get('peleador1', 'Local'))
            visitante = partido.get('peleador2', {}).get('nombre', partido.get('peleador2', 'Visitante'))
        else:
            local = partido.get('home', partido.get('local', 'Local'))
            visitante = partido.get('away', partido.get('visitante', 'Visitante'))

        recomendacion = analisis.get('recomendacion', 'N/A')
        confianza = analisis.get('confianza', 0)
        total = analisis.get('total_proyectado', 0)
        edge = analisis.get('edge', analisis.get('ev_mejor', 0))
        prob = analisis.get('probabilidad', confianza)

        prompt = f"""
Eres un analista profesional de apuestas deportivas con más de 15 años de experiencia. Eres conservador y solo recomiendas cuando hay **valor real**.

**Deporte:** {deporte.upper()}
**Partido:** {local} vs {visitante}

**Análisis del Motor v20:**
- Recomendación: {recomendacion}
- Confianza matemática: {confianza}%
- Probabilidad: {prob}%
- Total proyectado: {total}
- Edge: {edge:.1f}%

**Instrucciones:**
- Evalúa si el análisis matemático tiene sentido.
- Considera factores cualitativos importantes según el deporte (fatiga, lesiones, motivación, historial H2H, condiciones específicas).
- Sé honesto: si no hay valor claro, di "NO RECOMENDAR".
- Responde **solo** con el formato exacto.

MEJOR APUESTA FINAL: [OVER/UNDER/ML/SPREAD/BTTS/GANA LOCAL/GANA VISITANTE/NO RECOMENDAR]
PROBABILIDAD ESTIMADA: XX%
RAZÓN PRINCIPAL: [una línea clara y concreta]
RIESGO: [Bajo / Medio / Alto]
CONFIANZA IA: [Alta / Media / Baja]
"""

        try:
            response = self.model.generate_content(prompt)
            texto = response.text.strip()
            
            # Fallback si Gemini no sigue el formato
            if "MEJOR APUESTA FINAL" not in texto or len(texto) < 30:
                return f"""MEJOR APUESTA FINAL: {recomendacion}
PROBABILIDAD ESTIMADA: {confianza}%
RAZÓN PRINCIPAL: Análisis matemático sólido del motor v20
RIESGO: Medio
CONFIANZA IA: Media"""
            
            return texto
        except Exception as e:
            logger.error(f"Error Gemini: {e}")
            return f"""MEJOR APUESTA FINAL: {recomendacion}
PROBABILIDAD ESTIMADA: {confianza}%
RAZÓN PRINCIPAL: Error técnico en Gemini - confiando en motor
RIESGO: Medio
CONFIANZA IA: Media"""

    def analizar_con_decision(self, partido, analisis_heuristico):
        """Método de compatibilidad con tu código anterior"""
        return self.orquestrar_decision_final("NBA", partido, analisis_heuristico)

    def generar_proyeccion(self, prompt: str):
        """Genera proyección cuando faltan datos"""
        if not self.model:
            return None
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return None


def get_gemini(api_key=None):
    """Función helper para mantener compatibilidad"""
    return CerebroGeminiPro(api_key)
