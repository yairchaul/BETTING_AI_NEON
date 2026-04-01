# -*- coding: utf-8 -*-
"""
CEREBRO GEMINI PRO - Decisor Final con mejor manejo de errores
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
        self.api_key = api_key
        
        # Si no se pasó API key, intentar obtenerla
        if not self.api_key:
            try:
                if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
                    self.api_key = st.secrets['GEMINI_API_KEY']
                    st.sidebar.success("✅ Gemini key cargada desde secrets")
            except:
                pass
        
        if not self.api_key:
            try:
                with open('.env', 'r') as f:
                    for linea in f:
                        if 'GEMINI_API_KEY' in linea:
                            self.api_key = linea.split('=')[1].strip().strip('"').strip("'")
                            break
            except:
                pass
        
        if not self.api_key:
            logger.warning("❌ No hay API key de Gemini")
            self.model = None
            return

        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(modelo)
            logger.info(f"✅ Gemini Pro conectado ({modelo})")
        except Exception as e:
            logger.error(f"Error Gemini: {e}")
            self.model = None

    def orquestrar_decision_final(self, deporte: str, partido: Dict, analisis: Dict) -> str:
        """Decisor final inteligente con análisis de valor real"""
        if not self.model:
            return self._fallback_response(analisis)

        # Extraer nombres según deporte
        if deporte.upper() == "UFC":
            p1 = partido.get('peleador1', {})
            p2 = partido.get('peleador2', {})
            local = p1.get('nombre', partido.get('peleador1', 'Local')) if isinstance(p1, dict) else p1
            visitante = p2.get('nombre', partido.get('peleador2', 'Visitante')) if isinstance(p2, dict) else p2
        else:
            local = partido.get('home', partido.get('local', 'Local'))
            visitante = partido.get('away', partido.get('visitante', 'Visitante'))

        recomendacion = analisis.get('recomendacion', 'N/A')
        confianza = analisis.get('confianza', 0)
        total = analisis.get('total_proyectado', 0)
        edge = analisis.get('edge', 0)
        probabilidad = analisis.get('probabilidad', confianza)

        # Prompt simplificado para evitar errores
        prompt = f"""
Analiza este partido de {deporte.upper()}:
{local} vs {visitante}

Análisis del motor:
- Recomendación: {recomendacion}
- Confianza: {confianza}%
- Total proyectado: {total}
- Edge: {edge:.1f}%

Responde SOLO con este formato exacto:
MEJOR APUESTA FINAL: [apuesta]
PROBABILIDAD ESTIMADA: XX%
RAZÓN PRINCIPAL: [una línea]
RIESGO: [Bajo/Medio/Alto]
CONFIANZA IA: [Alta/Media/Baja]
"""

        try:
            response = self.model.generate_content(prompt)
            texto = response.text.strip()
            if "MEJOR APUESTA FINAL" in texto:
                return texto
            return self._fallback_response(analisis)
        except Exception as e:
            logger.error(f"Error en Gemini: {e}")
            return self._fallback_response(analisis)

    def _fallback_response(self, analisis):
        return f"""MEJOR APUESTA FINAL: {analisis.get('recomendacion', 'N/A')}
PROBABILIDAD ESTIMADA: {analisis.get('confianza', 50)}%
RAZÓN PRINCIPAL: Gemini no disponible - usando motor matemático
RIESGO: Medio
CONFIANZA IA: Media"""


def get_gemini(api_key=None):
    return CerebroGeminiPro(api_key)
