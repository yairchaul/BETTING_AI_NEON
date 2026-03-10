import streamlit as st
import re
import json

# Importación segura de Google Vision
try:
    from google.cloud import vision
    from google.oauth2 import service_account
    GOOGLE_VISION_AVAILABLE = True
except ModuleNotFoundError:
    GOOGLE_VISION_AVAILABLE = False
    vision = None
    service_account = None
    st.warning("⚠️ Google Vision no disponible. Instala con: pip install google-cloud-vision")

class ImageParser:
    def __init__(self):
        """Inicializa Google Vision usando st.secrets"""
        self.client = None
        self.team_names = {}

        if not GOOGLE_VISION_AVAILABLE:
            st.warning("⚠️ Google Vision no instalado. Usando modo de prueba.")
            return

        # Buscar credenciales en gcp_service_account (formato correcto)
        if "gcp_service_account" in st.secrets:
            try:
                creds = service_account.Credentials.from_service_account_info(
                    st.secrets["gcp_service_account"]
                )
                self.client = vision.ImageAnnotatorClient(credentials=creds)
                st.success("✅ Google Vision inicializado con gcp_service_account")
            except Exception as e:
                st.warning(f"⚠️ Error con gcp_service_account: {e}")
                self.client = None
        else:
            st.warning("⚠️ No hay credenciales de Google Vision. Usando modo de prueba.")
            self.client = None

    def normalize_name(self, name):
        if not name:
            return ""
        name = name.lower().strip()
        return re.sub(r"[^\w\s]", "", name)

    def get_full_team_name(self, partial_name):
        return partial_name.title()

    def process_image(self, image_bytes):
        """Procesa la imagen o devuelve datos de prueba si no hay Vision"""
        if not self.client:
            # Modo de prueba - devuelve partidos de ejemplo
            return [
                {"home": "Mazatlán FC", "away": "Club León", "all_odds": ["+215", "+250", "+120"]},
                {"home": "Necaxa", "away": "Pumas UNAM", "all_odds": ["+190", "+255", "+130"]},
                {"home": "Cruz Azul", "away": "Atlético San Luis", "all_odds": ["-223", "+340", "+600"]},
                {"home": "Querétaro FC", "away": "Club América", "all_odds": ["+320", "+240", "-112"]},
            ]

        try:
            image = vision.Image(content=image_bytes)
            response = self.client.document_text_detection(image=image)

            if response.error.message:
                st.error(f"Vision API error: {response.error.message}")
                return []

            if not response.text_annotations:
                return []

            words = []
            for ann in response.text_annotations[1:]:
                if ann.bounding_poly.vertices:
                    v = ann.bounding_poly.vertices
                    x = sum(p.x for p in v) / 4
                    y = sum(p.y for p in v) / 4
                    words.append({"text": ann.description, "x": x, "y": y})

            return self._group_by_visual_structure(words)

        except Exception as e:
            st.error(f"Error procesando imagen: {e}")
            return []

    def _group_by_visual_structure(self, words):
        if not words:
            return []
        words.sort(key=lambda w: w["y"])
        lines = []
        current = [words[0]]
        for w in words[1:]:
            if abs(w["y"] - current[-1]["y"]) < 15:
                current.append(w)
            else:
                current.sort(key=lambda x: x["x"])
                lines.append(" ".join(w["text"] for w in current))
                current = [w]
        if current:
            current.sort(key=lambda x: x["x"])
            lines.append(" ".join(w["text"] for w in current))
        return self._parse_matches(lines)

    def _parse_matches(self, lines):
        matches = []
        for line in lines:
            parts = line.split()
            odds = [p for p in parts if re.match(r"^[+-]?\d+\.?\d*$", p)]
            if len(odds) >= 3:
                matches.append({
                    "home": self.get_full_team_name(" ".join(parts[:1])),
                    "away": self.get_full_team_name(" ".join(parts[-2:])),
                    "all_odds": odds[:3]
                })
        return matches
