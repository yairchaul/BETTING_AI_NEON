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
        self.api_key = api_key or self._cargar_key()
        self.model = None
        self.model_name = None
        self.ultimo_error = None
        
        if not self.api_key:
            return

        self._conectar_estable()

    def _cargar_key(self):
        if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
            return st.secrets['GEMINI_API_KEY']
        return os.environ.get('GEMINI_API_KEY', '')

    def _conectar_estable(self):
        """Fuerza la conexión a modelos estables ignorando experimentales"""
        try:
            genai.configure(api_key=self.api_key)
            
            # 1. Obtener todos los modelos que REALMENTE responden
            modelos_disponibles = []
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        modelos_disponibles.append(m.name)
            except Exception:
                modelos_disponibles = []

            # 2. Lista de PRIORIDAD ESTABLE (Evitamos los que dicen 'exp' o '2.0' si dan problemas)
            # El 1.5-flash es el más estable y rápido actualmente.
            opciones = [
                'models/gemini-1.5-flash', 
                'models/gemini-1.5-pro',
                'models/gemini-pro'
            ]
            
            seleccion = None
            for opt in opciones:
                if opt in modelos_disponibles:
                    # Intento de validación real (si falla el 404 aquí, saltamos al siguiente)
                    try:
                        temp_model = genai.GenerativeModel(opt)
                        temp_model.generate_content("ping", generation_config={"max_output_tokens": 1})
                        seleccion = opt
                        break 
                    except Exception:
                        continue

            if not seleccion and modelos_disponibles:
                # Si ninguno de los preferidos funcionó, agarramos el primero que no sea experimental
                seleccion = next((m for m in modelos_disponibles if "-exp" not in m), modelos_disponibles[0])

            if seleccion:
                self.model_name = seleccion
                self.model = genai.GenerativeModel(
                    model_name=self.model_name,
                    generation_config={
                        "temperature": 0.2, # Más bajo = más estable
                        "max_output_tokens": 300,
                        "top_p": 0.8
                    }
                )
                logger.info(f"✅ Conectado a: {self.model_name}")
            else:
                self.ultimo_error = "No se hallaron modelos activos"

        except Exception as e:
            self.ultimo_error = str(e)

    def orquestrar_decision_final(self, deporte: str, partido: Dict, analisis: Dict) -> str:
        if not self.model:
            return self._fallback_response(analisis, f"IA no lista: {self.ultimo_error}")

        try:
            # Extraer nombres limpiamente
            l = self._get_n(partido, 'l')
            v = self._get_n(partido, 'v')
            
            prompt = f"""Analiza esta apuesta de {deporte}:
Evento: {l} vs {v}
Sugerencia: {analisis.get('recomendacion')}
Confianza: {analisis.get('confianza')}%
Edge: {analisis.get('edge')}%

Responde con este formato:
MEJOR APUESTA FINAL: [Apuesta]
PROBABILIDAD ESTIMADA: [XX]%
RAZÓN PRINCIPAL: [Breve]
RIESGO: [Bajo/Medio/Alto]
CONFIANZA IA: [Alta/Media/Baja]"""

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            # Si da 404 en plena ejecución, intentamos bajar al modelo más básico
            if "404" in str(e):
                self.model = genai.GenerativeModel('models/gemini-1.5-flash')
            return self._fallback_response(analisis, f"Error Gemini: {str(e)[:30]}")

    def _get_n(self, p, t):
        if t == 'l':
            res = p.get('home') or p.get('local') or p.get('peleador1', 'Local')
        else:
            res = p.get('away') or p.get('visitante') or p.get('peleador2', 'Visitante')
        return res.get('nombre', res) if isinstance(res, dict) else res

    def _fallback_response(self, analisis, motivo):
        return f"MEJOR APUESTA FINAL: {analisis.get('recomendacion')}\nPROBABILIDAD ESTIMADA: {analisis.get('confianza')}%\nRAZÓN PRINCIPAL: {motivo}\nRIESGO: Medio\nCONFIANZA IA: N/A"

def get_gemini(api_key=None):
    return CerebroGeminiPro(api_key)
