# modules/groq_vision.py
import base64
import streamlit as st
from groq import Groq
import json
import re

class GroqVisionParser:
    def __init__(self):
        """Inicializa el cliente de Groq"""
        self.client = Groq(api_key=st.secrets.get("GROQ_API_KEY", ""))
        # Modelo de visión actualizado (probamos con este)
        self.model = "llama-3.2-90b-vision-preview"  # Modelo actual
    
    def encode_image(self, image_bytes):
        """Convierte la imagen a base64"""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def extract_matches_with_vision(self, image_bytes):
        """
        Usa Groq Vision para extraer los partidos en formato estructurado
        """
        try:
            base64_image = self.encode_image(image_bytes)
            
            prompt = """
            Esta imagen contiene una tabla de apuestas de fútbol con múltiples partidos.
            Los partidos están organizados en este formato:
            
            [Equipo Local]
            [Cuota Local]
            Empate
            [Cuota Empate]
            [Equipo Visitante]
            [Cuota Visitante]
            
            Ejemplo:
            Bournemouth
            +148
            Empate
            +260
            Brentford
            +164
            
            Extrae TODOS los partidos que veas en la imagen y devuélvelos en formato JSON con esta estructura:
            [
              {
                "home": "nombre del equipo local",
                "away": "nombre del equipo visitante",
                "all_odds": ["cuota_local", "cuota_empate", "cuota_visitante"]
              }
            ]
            
            IMPORTANTE:
            - Incluye TODOS los partidos que aparezcan
            - Respeta el orden exacto de los equipos
            - Si ves "Empate" o "Empaté", es la palabra clave, no un equipo
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1,
                max_tokens=2000,
            )
            
            # Extraer el JSON de la respuesta
            content = response.choices[0].message.content
            
            # Limpiar la respuesta (a veces viene con markdown)
            content = re.sub(r'```json\s*|\s*```', '', content)
            content = re.sub(r'```\s*', '', content)
            
            # Buscar el patrón JSON en la respuesta
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                content = json_match.group()
            
            # Parsear JSON
            matches = json.loads(content)
            
            return matches
            
        except Exception as e:
            st.error(f"Error en Groq Vision: {e}")
            return []
