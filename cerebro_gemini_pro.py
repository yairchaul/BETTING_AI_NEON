# -*- coding: utf-8 -*-
"""
CEREBRO GEMINI PRO - Decisor Final con análisis de player props
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
            self.model = genai.GenerativeModel(modelo)
            logger.info(f"✅ Gemini Pro conectado ({modelo})")
        except Exception as e:
            logger.error(f"Error Gemini: {e}")
            self.model = None

    def orquestrar_decision_final(self, deporte: str, partido: Dict, analisis: Dict) -> str:
        """Decisor final con análisis de player props integrados"""
        if not self.model:
            return self._fallback_response(analisis)

        # Extraer nombres según deporte
        if deporte.upper() == "UFC":
            local = partido.get('peleador1', {}).get('nombre', partido.get('peleador1', 'Local'))
            visitante = partido.get('peleador2', {}).get('nombre', partido.get('peleador2', 'Visitante'))
        else:
            local = partido.get('home', partido.get('local', 'Local'))
            visitante = partido.get('away', partido.get('visitante', 'Visitante'))

        recomendacion = analisis.get('recomendacion', 'N/A')
        confianza = analisis.get('confianza', 0)
        
        # Construir insights de player props según deporte
        insights_text = ""
        
        if deporte.upper() == "NBA":
            top3_local = analisis.get('top_3pm_local')
            top3_visit = analisis.get('top_3pm_visit')
            if top3_local or top3_visit:
                insights_text = "\n**Jugadores destacados (3PM):**\n"
                if top3_local:
                    insights_text += f"- {local}: {top3_local.get('nombre', 'N/A')} ({top3_local.get('triples_por_partido', 0)} triples/partido, {top3_local.get('porcentaje_triples', 0):.1f}%)\n"
                if top3_visit:
                    insights_text += f"- {visitante}: {top3_visit.get('nombre', 'N/A')} ({top3_visit.get('triples_por_partido', 0)} triples/partido, {top3_visit.get('porcentaje_triples', 0):.1f}%)\n"
        
        elif deporte.upper() == "MLB":
            hr_local = analisis.get('top_hr_local')
            hr_visit = analisis.get('top_hr_visit')
            if hr_local or hr_visit:
                insights_text = "\n**Bateadores destacados (HR):**\n"
                if hr_local:
                    if isinstance(hr_local, list):
                        for h in hr_local[:2]:
                            insights_text += f"- {local}: {h.get('nombre', 'N/A')} ({h.get('hr', 0)} HR, AVG {h.get('avg', 0):.3f})\n"
                    else:
                        insights_text += f"- {local}: {hr_local.get('nombre', 'N/A')} ({hr_local.get('hr', 0)} HR)\n"
                if hr_visit:
                    if isinstance(hr_visit, list):
                        for h in hr_visit[:2]:
                            insights_text += f"- {visitante}: {h.get('nombre', 'N/A')} ({h.get('hr', 0)} HR, AVG {h.get('avg', 0):.3f})\n"
                    else:
                        insights_text += f"- {visitante}: {hr_visit.get('nombre', 'N/A')} ({hr_visit.get('hr', 0)} HR)\n"

        prompt = f"""
Eres un analista profesional de apuestas deportivas con más de 15 años de experiencia. Eres conservador y solo recomiendas cuando hay **valor real**.

**Deporte:** {deporte.upper()}
**Partido:** {local} vs {visitante}

**Análisis del Motor v20:**
- Recomendación: {recomendacion}
- Confianza matemática: {confianza}%
- Total proyectado: {analisis.get('total_proyectado', 'N/A')}
- Edge: {analisis.get('edge', 0):.1f}%

{insights_text}

**Instrucciones:**
- Evalúa si el análisis matemático tiene sentido.
- Considera los jugadores destacados mencionados y su impacto potencial.
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
            if "MEJOR APUESTA FINAL" in texto:
                return texto
            return self._fallback_response(analisis)
        except Exception as e:
            logger.error(f"Error Gemini: {e}")
            return self._fallback_response(analisis)

    def _fallback_response(self, analisis):
        return f"""MEJOR APUESTA FINAL: {analisis.get('recomendacion', 'N/A')}
PROBABILIDAD ESTIMADA: {analisis.get('confianza', 50)}%
RAZÓN PRINCIPAL: Gemini no disponible - usando motor matemático
RIESGO: Medio
CONFIANZA IA: Media"""


def get_gemini(api_key=None):
    return CerebroGeminiPro(api_key)
