# -*- coding: utf-8 -*-
"""
CEREBRO GEMINI PRO - Versión Adaptativa Anti-404
Elimina errores de modelos obsoletos detectando disponibilidad real.
"""
import os
import logging
import streamlit as st
import google.generativeai as genai
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CerebroGeminiPro:
    def __init__(self, api_key=None):
        self.api_key = api_key or self._cargar_key()
        self.model = None
        self.model_name = None
        self.ultimo_error = None
        
        if not self.api_key:
            logger.error("❌ No se encontró API key")
            return

        self._conectar_gemini()

    def _cargar_key(self):
        # Prioridad: st.secrets -> .env -> os.environ
        if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
            return st.secrets['GEMINI_API_KEY']
        return os.environ.get('GEMINI_API_KEY', '')

    def _conectar_gemini(self):
        try:
            genai.configure(api_key=self.api_key)
            
            # 1. Obtener modelos REALES disponibles en tu cuenta hoy
            modelos_reales = []
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        modelos_reales.append(m.name)
            except Exception as e:
                logger.error(f"Error listando modelos: {e}")
                modelos_reales = []

            # 2. Filtrar modelos que no sean obsoletos (evitar -exp si es posible)
            # Buscamos primero versiones estables de 1.5, luego flash, luego pro
            prioridad_busqueda = ['1.5-flash', '1.5-pro', '2.0-flash', 'gemini-pro']
            
            seleccionado = None
            for pref in prioridad_busqueda:
                for real in modelos_reales:
                    if pref in real and "-exp" not in real: # Preferir estables
                        seleccionado = real
                        break
                if seleccionado: break
            
            # Si no hay estables, cualquier cosa que funcione
            if not seleccionado and modelos_reales:
                seleccionado = modelos_reales[0]

            if not seleccionado:
                self.ultimo_error = "No hay modelos disponibles en esta API Key"
                return

            self.model_name = seleccionado
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={"temperature": 0.3, "max_output_tokens": 350}
            )
            logger.info(f"✅ Conectado a modelo activo: {self.model_name}")

        except Exception as e:
            self.ultimo_error = str(e)
            logger.error(f"❌ Error en conexión: {e}")

    def orquestrar_decision_final(self, deporte: str, partido: Dict, analisis: Dict) -> str:
        if not self.model:
            return self._fallback_response(analisis, f"IA Offline: {self.ultimo_error}")

        try:
            local = self._extraer_nombre(partido, 'local')
            visitante = self._extraer_nombre(partido, 'visitante')
            
            prompt = self._crear_prompt(
                deporte, local, visitante, 
                analisis.get('recomendacion', 'N/A'),
                analisis.get('confianza', 50),
                analisis.get('edge', 0)
            )

            response = self.model.generate_content(prompt)
            texto = response.text.strip()

            if "MEJOR APUESTA FINAL" in texto:
                return texto
            return self._fallback_response(analisis, "Respuesta con formato inválido")

        except Exception as e:
            # Si el error es un 404 (modelo caducado), intentamos reconectar una vez
            if "404" in str(e) or "not found" in str(e).lower():
                logger.warning("Modelo detectado como obsoleto. Intentando refrescar lista...")
                self._conectar_gemini()
            return self._fallback_response(analisis, f"Error Gemini: {str(e)[:40]}")

    def _extraer_nombre(self, partido, tipo):
        if tipo == 'local':
            return partido.get('home', partido.get('local', partido.get('peleador1', {} if isinstance(partido.get('peleador1'), dict) else 'Local')))
        return partido.get('away', partido.get('visitante', partido.get('peleador2', {} if isinstance(partido.get('peleador2'), dict) else 'Visitante')))

    def _crear_prompt(self, deporte, local, vis, rec, conf, edge):
        return f"""Analista Pro: {deporte}
Evento: {local} vs {vis}
Motor Estadístico: {rec} (Confianza: {conf}%, Edge: {edge}%)

Instrucciones:
1. Valida si hay valor real.
2. Formato ESTRICTO:
MEJOR APUESTA FINAL: [Apuesta]
PROBABILIDAD ESTIMADA: [XX]%
RAZÓN PRINCIPAL: [1 línea]
RIESGO: [Bajo/Medio/Alto]
CONFIANZA IA: [Alta/Media/Baja]"""

    def _fallback_response(self, analisis, motivo):
        return f"""MEJOR APUESTA FINAL: {analisis.get('recomendacion', 'N/A')}
PROBABILIDAD ESTIMADA: {analisis.get('confianza', 50)}%
RAZÓN PRINCIPAL: {motivo} (Motor Matemático)
RIESGO: Medio
CONFIANZA IA: N/A"""

def get_gemini(api_key=None):
    return CerebroGeminiPro(api_key)
