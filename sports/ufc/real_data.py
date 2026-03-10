import streamlit as st

class UFCRealData:
    # Extrae datos reales de UFC de múltiples fuentes
    
    def __init__(self):
        pass
    
    def get_event_details(self, event_name='UFC Fight Night: Emmett vs. Vallejos'):
        # Obtiene todas las peleas de un evento con datos de tu captura
        try:
            # Datos extraídos de tu captura de imagen
            peleas = [
                {
                    'fighter1': 'Josh Emmett', 
                    'fighter2': 'Kevin Vallejos',
                    'odds1': 400,
                    'odds2': -625,
                    'records': ('19-6-0', '17-1-0'),
                    'age': (41, 24),
                    'reach': (178, 173)
                },
                {
                    'fighter1': 'Piera Rodriguez',
                    'fighter2': 'Sam Hughes',
                    'odds1': -154,
                    'odds2': 120,
                    'records': ('11-2-0', '11-6-0'),
                },
                {
                    'fighter1': 'Elijah Smith',
                    'fighter2': 'Su Young You',
                    'odds1': -209,
                    'odds2': 165,
                },
                {
                    'fighter1': 'Bia Mesquita',
                    'fighter2': 'Montserrat Rendon',
                    'odds1': -550,
                    'odds2': 375,
                },
                {
                    'fighter1': 'Luan Lacerda',
                    'fighter2': 'Hecher Sosa',
                    'odds1': 180,
                    'odds2': -239,
                },
                {
                    'fighter1': 'Bolaji Oki',
                    'fighter2': 'Manoel Sousa',
                    'odds1': 200,
                    'odds2': -264,
                },
                {
                    'fighter1': 'Chris Curtis',
                    'fighter2': 'Myktybek Orolbai',
                    'odds1': 210,
                    'odds2': -286,
                },
                {
                    'fighter1': 'Brad Tavares',
                    'fighter2': 'Eryk Anders',
                    'odds1': -143,
                    'odds2': 110,
                },
                {
                    'fighter1': 'Charles Johnson',
                    'fighter2': 'Bruno Silva',
                    'odds1': -209,
                    'odds2': 162,
                },
                {
                    'fighter1': 'Vitor Petrino',
                    'fighter2': 'Steven Asplund',
                    'odds1': -264,
                    'odds2': 200,
                },
                {
                    'fighter1': 'Marwan Rahiki',
                    'fighter2': 'Harry Hardwick',
                    'odds1': -286,
                    'odds2': 210,
                },
                {
                    'fighter1': 'Andre Fili',
                    'fighter2': 'Jose Delgado',
                    'odds1': 265,
                    'odds2': -350,
                },
                {
                    'fighter1': 'Ion Cutelaba',
                    'fighter2': 'Oumar Sy',
                    'odds1': 190,
                    'odds2': -250,
                },
                {
                    'fighter1': 'Amanda Lemos',
                    'fighter2': 'Gillian Robertson',
                    'odds1': 160,
                    'odds2': -209,
                },
            ]
            return peleas
        except Exception as e:
            st.warning(f'Error cargando datos UFC: {e}')
            return []
