# modules/groq_vision.py
import base64
import streamlit as st
from groq import Groq
import json
import re

class GroqVisionParser:
    def __init__(self):
        """Inicializa el cliente de Groq y verifica modelos disponibles"""
        self.client = Groq(api_key=st.secrets.get("GROQ_API_KEY", ""))
        self.model = self._get_available_vision_model()
    
    def _get_available_vision_model(self):
        """Obtiene el primer modelo de visión disponible"""
        try:
            # Listar modelos disponibles
            models = self.client.models.list()
            vision_models = []
            
            for model in models.data:
                # Filtrar modelos de visión (generalmente tienen "vision" en el ID)
                if 'vision' in model.id:
                    vision_models.append(model.id)
            
            if vision_models:
                st.info(f"📸 Modelos de visión disponibles: {', '.join(vision_models)}")
                return vision_models[0]  # Usar el primero disponible
            else:
                st.warning("⚠️ No se encontraron modelos de visión. Usando fallback.")
                return None
        except Exception as e:
            st.error(f"Error consultando modelos: {e}")
            return None
    
    def encode_image(self, image_bytes):
        """Convierte la imagen a base64"""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def extract_matches_with_vision(self, image_bytes):
        """
        Usa Groq Vision para extraer los partidos
        """
        if not self.model:
            st.warning("No hay modelo de visión disponible")
            return []
        
        try:
            base64_image = self.encode_image(image_bytes)
            
            prompt = """
            Esta imagen contiene una tabla de apuestas de fútbol con este formato:
            
            [Equipo Local] [Cuota Local] [Empate] [Cuota Empate] [Equipo Visitante]
            
            Ejemplo:
            Pacha -110 Empate +260 Necaxa
            
            Extrae TODOS los partidos y devuélvelos en JSON:
            [
              {
                "home": "equipo local",
                "away": "equipo visitante",
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
                max_tokens=2000,
            )
            
            content = response.choices[0].message.content
            content = re.sub(r'```json\s*|\s*```', '', content)
            content = re.sub(r'```\s*', '', content)
            
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                content = json_match.group()
            
            return json.loads(content)
            
        except Exception as e:
            st.error(f"Error en Groq Vision: {e}")
            return []
