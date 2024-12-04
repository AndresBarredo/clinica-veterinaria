import pandas as pd
import streamlit as st
import requests

API_URL = "http://fastapi:8000"

@st.cache_data
def obtener_estadisticas():
    response = requests.get(f"{API_URL}/estadisticas/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error al obtener estadísticas.")
        return None

def actualizar_estadisticas():
    response = requests.post(f"{API_URL}/actualizar_estadisticas/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error al actualizar estadísticas.")
        return None

# Cargar estadísticas iniciales
estadisticas = obtener_estadisticas()

st.title("Dashboard de Seguimiento")

if estadisticas:
    st.header("Estadísticas Generales")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.subheader('🐶 Dueños Registrados')
        st.markdown(f"<h1 style='text-align: center;'>{estadisticas['dueños']}</h1>", unsafe_allow_html=True)

    with col2:
        st.subheader('🐾 Mascotas Registradas')
        st.markdown(f"<h1 style='text-align: center;'>{estadisticas['mascotas']}</h1>", unsafe_allow_html=True)

    with col3:
        st.subheader('📆 Citas Registradas')
        st.markdown(f"<h1 style='text-align: center;'>{estadisticas['citas']}</h1>", unsafe_allow_html=True)

    with col4:
        st.subheader('💸 Ingresos Totales')
        st.markdown(f"<h1 style='text-align: center;'>${estadisticas['ingresos']:.2f}</h1>", unsafe_allow_html=True)

    with col5:
        st.subheader('🧾 Recibos Generados')
        st.markdown(f"<h1 style='text-align: center;'>{estadisticas['recibos']}</h1>", unsafe_allow_html=True)

    # Botón para actualizar estadísticas
    if st.button("Actualizar Estadísticas"):
        nuevas_estadisticas = actualizar_estadisticas()
        if nuevas_estadisticas:
            estadisticas = nuevas_estadisticas
            st.success("Estadísticas actualizadas correctamente.")
        else:
            st.error("Error al actualizar estadísticas.")
else:
    st.error("No se pudieron cargar las estadísticas.")
