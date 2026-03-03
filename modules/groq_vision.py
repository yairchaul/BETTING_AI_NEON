# modules/groq_vision.py
import base64
import streamlit as st
from groq import Groq
import json
import re

class GroqVisionParser:
    def __init__(self):
        """Inicializa con el modelo estable para evitar el error 400."""
        self.client = Groq(api_key=st.secrets.get("GROQ_API_KEY", ""))
        # Único modelo de visión estable y soportado actualmente
        self.model = "llama-3.2-11b-vision-instant"

    def encode_image(self, image_bytes):
        """Convierte la imagen a base64."""
        return base64.b64encode(image_bytes).decode('utf-8')

    def extract_matches_with_vision(self, image_bytes):
        """
        Extrae partidos ignorando cuotas bloqueadas y limpiando nombres.
        """
        if not self.client.api_key:
            return []

        try:
            base64_image = self.encode_image(image_bytes)

            # Prompt ultra-específico para el formato de tu imagen
            prompt = """
            Analiza esta imagen de apuestas deportivas. 
            Busca bloques de partidos. Un partido tiene: Equipo 1, Equipo 2 y tres cuotas (1, X, 2).
            
            INSTRUCCIONES CRÍTICAS:
            1. Los nombres pueden tener (M), (W) o (R). Quita esos paréntesis para el JSON.
            2. Las cuotas son números con signo (ej: +125, -163).
            3. Si en lugar de número ves un icono de candado o la letra 'A', usa "LOCKED".
            4. Si un partido tiene cuotas "LOCKED", inclúyelo pero marca las cuotas así.

            Devuelve exclusivamente este formato JSON:
            [
              {
                "home": "Melbourne City",
                "away": "Buriram United",
                "all_odds": ["+125", "+220", "+200"]
              }
            ]
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }],
                temperature=0,
            )

            content = response.choices[0].message.content
            
            # Limpieza de la respuesta
            content = re.sub(r'```json\s*|\s*```|```', '', content)
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            
            if json_match:
                raw_matches = json.loads(json_match.group())
                
                # VALIDACIÓN Y FILTRADO
                final_matches = []
                for m in raw_matches:
                    # Si alguna cuota es LOCKED o no es un formato válido, avisamos
                    if any(val == "LOCKED" or "A" in str(val) for val in m['all_odds']):
                        st.warning(f"🚫 Omitido: {m['home']} vs {m['away']} (Cuotas bloqueadas)")
                    else:
                        final_matches.append(m)
                
                return final_matches
            
            return []

        except Exception as e:
            st.error(f"Error crítico en Groq Vision: {e}")
            return []
