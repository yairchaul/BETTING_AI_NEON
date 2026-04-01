# -*- coding: utf-8 -*-
"""
CEREBRO GEMINI PRO - Decisor Final Inteligente (Versión Optimizada 2026)
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
            logger.info(f"✅ Gemini Pro conectado ({modelo})")
        except Exception as e:
            logger.error(f"Error: {e}")
            self.model = None

    def orquestrar_decision_final(self, deporte: str, partido: Dict, analisis_heuristico: Dict) -> str:
        if not self.model:
            return "❌ Gemini no disponible - confiando en análisis matemático"

        if deporte.lower() == "ufc":
            local = partido.get('peleador1', {}).get('nombre', 'Desconocido')
            visitante = partido.get('peleador2', {}).get('nombre', 'Desconocido')
        else:
            local = partido.get('home', partido.get('local', 'Desconocido'))
            visitante = partido.get('away', partido.get('visitante', 'Desconocido'))

        recomendacion = analisis_heuristico.get('recomendacion', 'N/A')
        confianza_math = analisis_heuristico.get('confianza', 0)
        total_proyectado = analisis_heuristico.get('total_proyectado', 0)
        edge = analisis_heuristico.get('edge', analisis_heuristico.get('ev_mejor', 0))

        prompt = f"""
Eres un analista profesional de apuestas deportivas con más de 15 años de experiencia.

**Deporte:** {deporte.upper()}
**Partido:** {local} vs {visitante}

**Análisis Matemático (Motor v20):**
- Recomendación: {recomendacion}
- Confianza matemática: {confianza_math}%
- Total proyectado: {total_proyectado}
- Edge calculado: {edge:.1f}%

**Cuotas:** {partido.get('odds', 'No disponibles')}

Responde EXCLUSIVAMENTE con este formato:

MEJOR APUESTA FINAL: [OVER/UNDER/ML/SPREAD/BTTS/NO RECOMENDAR]
PROBABILIDAD ESTIMADA: XX%
RAZÓN PRINCIPAL: [máximo una línea]
RIESGO: [Bajo / Medio / Alto]
CONFIANZA IA: [Alta / Media / Baja]
"""
        try:
            response = self.model.generate_content(prompt)
            texto = response.text.strip()
            if "MEJOR APUESTA FINAL" not in texto or len(texto) < 30:
                return f"""MEJOR APUESTA FINAL: {recomendacion}
PROBABILIDAD ESTIMADA: {confianza_math}%
RAZÓN PRINCIPAL: Análisis matemático sólido del motor v20
RIESGO: Medio
CONFIANZA IA: Media"""
            return texto
        except Exception as e:
            logger.error(f"Error Gemini: {e}")
            return f"""MEJOR APUESTA FINAL: {recomendacion}
PROBABILIDAD ESTIMADA: {confianza_math}%
RAZÓN PRINCIPAL: Error en Gemini - confiando en motor matemático
RIESGO: Medio
CONFIANZA IA: Media"""

    def analizar_con_decision(self, partido, analisis_heuristico):
        return self.orquestrar_decision_final("NBA", partido, analisis_heuristico)

    def generar_proyeccion(self, prompt: str):
        if not self.model:
            return None
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return None

def get_gemini(api_key=None):
    return CerebroGeminiPro(api_key)
