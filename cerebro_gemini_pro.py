# -*- coding: utf-8 -*-
import os
import logging
import streamlit as st
import google.generativeai as genai
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CerebroGeminiPro:
    def __init__(self, api_key=None):
        # 1. Cargar API Key
        self.api_key = api_key
        if not self.api_key:
            if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
                self.api_key = st.secrets['GEMINI_API_KEY']
            else:
                self.api_key = os.environ.get('GEMINI_API_KEY', '')

        self.model = None
        self.model_name = "models/gemini-1.5-flash" # FORZAMOS EL ESTABLE
        
        if self.api_key:
            self._conectar_seguro()

    def _conectar_seguro(self):
        try:
            genai.configure(api_key=self.api_key)
            # Configuramos el modelo estable directamente
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 250,
                }
            )
            # Prueba real de vida
            self.model.generate_content("ok", generation_config={"max_output_tokens": 1})
            logger.info(f"✅ Conectado a {self.model_name}")
        except Exception as e:
            logger.error(f"❌ Error crítico: {e}")
            self.model = None

    def orquestrar_decision_final(self, deporte: str, partido: Dict, analisis: Dict) -> str:
        # Si el modelo falló al conectar, usamos fallback inmediato
        if not self.model:
            return self._fallback_response(analisis, "IA Desconectada (Revisa API Key)")

        try:
            # Extraer nombres de equipos/peleadores
            local = self._limpiar_nombre(partido, 'local')
            visitante = self._limpiar_nombre(partido, 'visitante')
            
            prompt = f"""Analista Pro: {deporte}
Evento: {local} vs {visitante}
Motor: {analisis.get('recomendacion')}
Confianza: {analisis.get('confianza')}%

Responde con este formato exacto:
MEJOR APUESTA FINAL: [Apuesta]
PROBABILIDAD ESTIMADA: [XX]%
RAZÓN PRINCIPAL: [Una frase]
RIESGO: [Bajo/Medio/Alto]
CONFIANZA IA: [Alta/Media/Baja]"""

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            return self._fallback_response(analisis, f"Error: Modelo 1.5 en pausa")

    def _limpiar_nombre(self, p, tipo):
        try:
            if tipo == 'local':
                n = p.get('home') or p.get('local') or p.get('peleador1', 'Local')
            else:
                n = p.get('away') or p.get('visitante') or p.get('peleador2', 'Visitante')
            
            if isinstance(n, dict): return n.get('nombre', 'Equipo')
            return str(n)
        except: return "Equipo"

    def _fallback_response(self, analisis, motivo):
        return (f"MEJOR APUESTA FINAL: {analisis.get('recomendacion', 'N/A')}\n"
                f"PROBABILIDAD ESTIMADA: {analisis.get('confianza', 50)}%\n"
                f"RAZÓN PRINCIPAL: {motivo}\n"
                f"RIESGO: Medio\n"
                f"CONFIANZA IA: N/A")

def get_gemini(api_key=None):
    return CerebroGeminiPro(api_key)
