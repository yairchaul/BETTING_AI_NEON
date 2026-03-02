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
        self.model = "llama-3.2-90b-vision-preview"
    
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
            Esta imagen contiene una tabla de apuestas de fútbol con 5 partidos.
            La tabla tiene 6 columnas:
            1. Equipo Local
            2. Cuota Local (formato americano: +178, -278, etc)
            3. La palabra "Empate"
            4. Cuota de Empate (formato americano)
            5. Equipo Visitante
            6. Cuota Visitante (formato americano)

            Extrae SOLO los 5 partidos y devuélvelos en formato JSON con esta estructura exacta:
            [
              {
                "local": "nombre del equipo local",
                "cuota_local": "valor con signo",
                "empate": "Empate",
                "cuota_empate": "valor con signo",
                "visitante": "nombre del equipo visitante",
                "cuota_visitante": "valor con signo"
              }
            ]

            Asegúrate de incluir SOLO los 5 partidos principales.
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
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            content = re.sub(r'```json\s*|\s*```', '', content)
            matches = json.loads(content)
            
            formatted_matches = []
            for m in matches:
                formatted_matches.append({
                    "home": m["local"],
                    "away": m["visitante"],
                    "all_odds": [
                        m["cuota_local"],
                        m["cuota_empate"],
                        m["cuota_visitante"]
                    ]
                })
            
            return formatted_matches
            
        except Exception as e:
            st.error(f"Error en Groq Vision: {e}")
            return []
