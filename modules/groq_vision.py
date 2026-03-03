# modules/groq_vision.py
import base64
import streamlit as st
from groq import Groq
import json
import re

class GroqVisionParser:
    def __init__(self):
        """Inicializa el cliente de Groq y define el modelo de visión."""
        self.client = Groq(api_key=st.secrets.get("GROQ_API_KEY", ""))
        # Forzamos el modelo activo para evitar el error 400 del modelo decommisioned
        self.model = "llama-3.2-11b-vision-preview"

    def encode_image(self, image_bytes):
        """Convierte la imagen a base64."""
        return base64.b64encode(image_bytes).decode('utf-8')

    def extract_matches_with_vision(self, image_bytes):
        """
        Usa Groq Vision para extraer los partidos en formato estructurado.
        """
        if not self.client:
            st.error("API Key de Groq no configurada.")
            return []

        try:
            base64_image = self.encode_image(image_bytes)

            prompt = """
            Esta imagen contiene una tabla de apuestas de fútbol con múltiples partidos.
            Extrae TODOS los partidos que veas y devuélvelos estrictamente en formato JSON:
            [
              {
                "home": "nombre del equipo local",
                "away": "nombre del equipo visitante",
                "all_odds": ["cuota_local", "cuota_empate", "cuota_visitante"]
              }
            ]
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
                max_tokens=4000,
            )

            content = response.choices[0].message.content
            # Limpieza de formato Markdown si el modelo lo incluye
            content = re.sub(r'```json\s*|\s*```', '', content)
            
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                content = json_match.group()

            return json.loads(content)

        except Exception as e:
            st.error(f"Error en Groq Vision: {e}")
            return []
