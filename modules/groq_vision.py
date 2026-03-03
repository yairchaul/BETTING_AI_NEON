# modules/groq_vision.py
import base64
import streamlit as st
from groq import Groq
import json
import re
import time

class GroqVisionParser:
    def __init__(self):
        """Inicializa el cliente de Groq con fallback silencioso"""
        self.api_key = st.secrets.get("GROQ_API_KEY", "")
        self.client = None
        self.model = None
        self.is_available = False
        self.available_models = []
        
        if self.api_key:
            self._initialize_with_retry()
    
    def _initialize_with_retry(self, max_retries=2):
        for attempt in range(max_retries):
            try:
                self.client = Groq(api_key=self.api_key)
                self._fetch_available_models()
                
                if self.available_models:
                    self.model = self.available_models[0]
                    self.is_available = True
                    return
            except:
                pass
            time.sleep(0.5)
        self.is_available = False
    
    def _fetch_available_models(self):
        try:
            models = self.client.models.list()
            vision_keywords = ['vision', 'llama-3.2', 'llava']
            self.available_models = [
                m.id for m in models.data 
                if any(keyword in m.id.lower() for keyword in vision_keywords)
            ]
            preferred = ['llama-3.2-90b-vision-preview', 'llama-3.2-11b-vision-preview']
            self.available_models.sort(key=lambda x: (
                -preferred.index(x) if x in preferred else 0
            ))
        except:
            self.available_models = []
    
    def encode_image(self, image_bytes):
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def extract_matches_with_vision(self, image_bytes):
        if not self.is_available or not self.model:
            return None
        
        prompts = [
            """Extrae los partidos de fútbol. Cada uno tiene: Local, Cuota L, "Empate", Cuota E, Visitante, Cuota V.
            Devuelve JSON con objetos {home, away, all_odds}.""",
            
            """La imagen contiene líneas con formato: [Local] [Cuota L] [Empate] [Cuota E] [Visitante] [Cuota V].
            Extrae todos en JSON."""
        ]
        
        for prompt in prompts:
            try:
                base64_image = self.encode_image(image_bytes)
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                                }
                            ]
                        }
                    ],
                    temperature=0.1,
                    max_tokens=4000,
                )
                
                content = response.choices[0].message.content
                content = re.sub(r'```json\s*|\s*```', '', content)
                
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    content = json_match.group()
                
                matches = json.loads(content)
                if matches and len(matches) > 0:
                    return matches
                    
            except:
                continue
        
        return None
