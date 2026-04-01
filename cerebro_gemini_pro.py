# -*- coding: utf-8 -*-
import os
import logging
import streamlit as st
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CerebroGeminiPro:
    def __init__(self, api_key=None):
        self.api_key = api_key or self._get_key()
        self.model = None
        self.model_name = None
        
        if self.api_key:
            self._inicializar_adaptativo()

    def _get_key(self):
        if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
            return st.secrets['GEMINI_API_KEY']
        return os.environ.get('GEMINI_API_KEY', '')

    def _inicializar_adaptativo(self):
        """Prueba modelos en orden de potencia hasta que uno responda (evita 404)"""
        genai.configure(api_key=self.api_key)
        
        # Lista de candidatos (del más nuevo al más estable)
        candidatos = [
            'gemini-2.0-flash', 
            'gemini-1.5-pro', 
            'gemini-1.5-flash', 
            'gemini-pro'
        ]
        
        for nombre in candidatos:
            try:
                # Intentamos instanciar y hacer una mini-prueba de vida
                test_model = genai.GenerativeModel(nombre)
                # Si esto no da error 404, es que el modelo está activo para tu cuenta
                test_model.generate_content("C", generation_config={"max_output_tokens": 1})
                
                self.model = test_model
                self.model_name = nombre
                logger.info(f"✅ Modelo adaptado con éxito: {nombre}")
                break # Salimos del bucle al encontrar el primero que funciona
            except Exception as e:
                logger.warning(f"⚠️ El modelo {nombre} no está disponible (Error: {str(e)[:20]}). Probando siguiente...")
                continue

    def orquestrar_decision_final(self, deporte, partido, analisis):
        # Si después de todo no hay modelo, fallback
        if not self.model:
            return self._fallback_response(analisis, "No se encontró ningún modelo Gemini activo")

        try:
            local = self._fix_name(partido, 'l')
            vis = self._fix_name(partido, 'v')
            
            prompt = f"""Analiza: {deporte} | {local} vs {vis}
Motor: {analisis.get('recomendacion')} | Confianza: {analisis.get('confianza')}%
            
Responde breve:
MEJOR APUESTA FINAL: [Apuesta]
PROBABILIDAD ESTIMADA: [XX]%
RAZÓN PRINCIPAL: [Lógica]
RIESGO: [Bajo/Medio/Alto]
CONFIANZA IA: [Alta/Media/Baja]"""

            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            # Si el modelo muere en medio de la ejecución, intentamos recuperarlo
            self._inicializar_adaptativo()
            return self._fallback_response(analisis, f"Re-adaptando modelo... ({str(e)[:30]})")

    def _fix_name(self, p, t):
        key = 'home' if t == 'l' else 'away'
        alt = 'peleador1' if t == 'l' else 'peleador2'
        val = p.get(key) or p.get('local' if t == 'l' else 'visitante') or p.get(alt, 'Equipo')
        return val.get('nombre', val) if isinstance(val, dict) else str(val)

    def _fallback_response(self, analisis, motivo):
        return (f"MEJOR APUESTA FINAL: {analisis.get('recomendacion')}\n"
                f"PROBABILIDAD ESTIMADA: {analisis.get('confianza')}%\n"
                f"RAZÓN PRINCIPAL: {motivo}\nRIESGO: Medio\nCONFIANZA IA: N/A")

def get_gemini(api_key=None):
    return CerebroGeminiPro(api_key)
