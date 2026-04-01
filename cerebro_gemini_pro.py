# -*- coding: utf-8 -*-
"""
CEREBRO GEMINI PRO - Decisor Final Inteligente
Versión definitiva con modelos correctos de Gemini
"""

import os
import logging
import streamlit as st
import google.generativeai as genai
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CerebroGeminiPro:
    def __init__(self, api_key=None, modelo="gemini-2.0-flash-exp"):
        """
        Inicializa Gemini con la API key desde múltiples fuentes
        MODELOS DISPONIBLES:
        - gemini-2.0-flash-exp (recomendado)
        - gemini-1.5-pro
        - gemini-1.5-flash
        """
        self.api_key = None
        
        # 1. Intentar con la API key pasada como argumento
        if api_key:
            self.api_key = api_key
            logger.info("API key recibida como argumento")
        
        # 2. Intentar con st.secrets (Streamlit Cloud)
        if not self.api_key:
            try:
                if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
                    self.api_key = st.secrets['GEMINI_API_KEY']
                    if self.api_key:
                        logger.info("API key cargada desde st.secrets")
            except Exception as e:
                logger.warning(f"Error leyendo secrets: {e}")
        
        # 3. Intentar con archivo .env (local)
        if not self.api_key:
            try:
                with open('.env', 'r') as f:
                    for linea in f:
                        if 'GEMINI_API_KEY' in linea:
                            self.api_key = linea.split('=')[1].strip().strip('"').strip("'")
                            if self.api_key:
                                logger.info("API key cargada desde .env")
                                break
            except Exception as e:
                logger.warning(f"Error leyendo .env: {e}")
        
        # 4. Intentar con variable de entorno
        if not self.api_key:
            self.api_key = os.environ.get('GEMINI_API_KEY', '')
            if self.api_key:
                logger.info("API key cargada desde variable de entorno")
        
        # Verificar si tenemos API key
        if not self.api_key:
            logger.error("❌ No se encontró API key de Gemini")
            self.model = None
            return
        
        # Configurar Gemini con modelo correcto
        try:
            genai.configure(api_key=self.api_key)
            
            # Listar modelos disponibles para debug
            try:
                modelos = genai.list_models()
                modelos_disponibles = [m.name for m in modelos if 'gemini' in m.name]
                logger.info(f"Modelos disponibles: {modelos_disponibles[:5]}")
            except:
                pass
            
            # Usar modelo recomendado
            self.model = genai.GenerativeModel(
                model_name=modelo,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 300,
                    "top_p": 0.95
                }
            )
            logger.info(f"✅ Gemini Pro conectado exitosamente ({modelo})")
        except Exception as e:
            logger.error(f"❌ Error conectando Gemini: {e}")
            self.model = None

    def orquestrar_decision_final(self, deporte: str, partido: Dict, analisis: Dict) -> str:
        """
        Decisor final inteligente con análisis de valor real
        """
        if not self.model:
            return self._fallback_response(analisis, "Gemini no disponible")
        
        try:
            # Extraer nombres según deporte
            local = self._extraer_nombre_local(deporte, partido)
            visitante = self._extraer_nombre_visitante(deporte, partido)
            
            # Extraer datos del análisis
            recomendacion = analisis.get('recomendacion', 'N/A')
            confianza = analisis.get('confianza', 50)
            total = analisis.get('total_proyectado', 'N/A')
            edge = analisis.get('edge', 0)
            probabilidad = analisis.get('probabilidad', confianza)
            
            # Crear prompt optimizado
            prompt = self._crear_prompt(deporte, local, visitante, recomendacion, confianza, total, edge, probabilidad)
            
            # Llamar a Gemini
            response = self.model.generate_content(prompt)
            texto = response.text.strip()
            
            # Validar respuesta
            if self._validar_respuesta(texto):
                return texto
            
            # Si la respuesta no tiene el formato esperado, usar fallback
            logger.warning("Respuesta de Gemini con formato incorrecto, usando fallback")
            return self._fallback_response(analisis, "Formato de respuesta incorrecto")
            
        except Exception as e:
            logger.error(f"Error en Gemini: {e}")
            return self._fallback_response(analisis, f"Error técnico: {str(e)[:50]}")

    def _extraer_nombre_local(self, deporte: str, partido: Dict) -> str:
        """Extrae el nombre del equipo/peleador local"""
        if deporte.upper() == "UFC":
            p1 = partido.get('peleador1', {})
            if isinstance(p1, dict):
                return p1.get('nombre', partido.get('peleador1', 'Local'))
            return str(p1)
        return partido.get('home', partido.get('local', 'Local'))

    def _extraer_nombre_visitante(self, deporte: str, partido: Dict) -> str:
        """Extrae el nombre del equipo/peleador visitante"""
        if deporte.upper() == "UFC":
            p2 = partido.get('peleador2', {})
            if isinstance(p2, dict):
                return p2.get('nombre', partido.get('peleador2', 'Visitante'))
            return str(p2)
        return partido.get('away', partido.get('visitante', 'Visitante'))

    def _crear_prompt(self, deporte, local, visitante, recomendacion, confianza, total, edge, probabilidad):
        """Crea el prompt optimizado para Gemini"""
        return f"""
Eres un analista profesional de apuestas deportivas con 15 años de experiencia.

**Deporte:** {deporte.upper()}
**Partido:** {local} vs {visitante}

**Análisis del Motor:**
- Recomendación: {recomendacion}
- Confianza matemática: {confianza}%
- Probabilidad: {probabilidad}%
- Total proyectado: {total}
- Edge: {edge:.1f}%

**Instrucciones:**
- Analiza si la recomendación tiene valor real
- Sé honesto: si no hay valor claro, di "NO RECOMENDAR"
- Responde SOLO con este formato exacto (sin texto adicional):

MEJOR APUESTA FINAL: [apuesta]
PROBABILIDAD ESTIMADA: XX%
RAZÓN PRINCIPAL: [una línea clara]
RIESGO: [Bajo/Medio/Alto]
CONFIANZA IA: [Alta/Media/Baja]
"""

    def _validar_respuesta(self, texto: str) -> bool:
        """Valida que la respuesta tenga el formato esperado"""
        return all(key in texto for key in ["MEJOR APUESTA FINAL", "PROBABILIDAD ESTIMADA", "RAZÓN PRINCIPAL", "RIESGO", "CONFIANZA IA"])

    def _fallback_response(self, analisis: Dict, motivo: str = "Fallback") -> str:
        """Respuesta de respaldo cuando Gemini no está disponible"""
        recomendacion = analisis.get('recomendacion', 'N/A')
        confianza = analisis.get('confianza', 50)
        
        return f"""MEJOR APUESTA FINAL: {recomendacion}
PROBABILIDAD ESTIMADA: {confianza}%
RAZÓN PRINCIPAL: {motivo} - usando motor matemático
RIESGO: Medio
CONFIANZA IA: Media"""

    def analizar_con_decision(self, partido, analisis_heuristico):
        """Método de compatibilidad"""
        return self.orquestrar_decision_final("NBA", partido, analisis_heuristico)


def get_gemini(api_key=None):
    """Función helper para mantener compatibilidad"""
    return CerebroGeminiPro(api_key)
