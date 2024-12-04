import streamlit as st
import requests

# URL del microservicio FastAPI
API_URL = "http://fastapi:8000"

# Función para obtener las estadísticas
def obtener_estadisticas():
    response = requests.get(f"{API_URL}/estadisticas/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error al obtener estadísticas.")
        return None

# Inicializar el Dashboard
st.title("Dashboard de Seguimiento y Actualización 🐾")

# Sección de estadísticas
st.header("Estadísticas Generales")

# Botón para actualizar estadísticas
if st.button("Actualizar Estadísticas"):
    estadisticas = obtener_estadisticas()

    # Mostrar estadísticas actualizadas
    if estadisticas:
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
    else:
        st.error("No se pudieron cargar las estadísticas. Presiona el botón para reintentar.")
else:
    # Mostrar mensaje inicial o por defecto
    st.info("Presiona el botón 'Actualizar Estadísticas' para cargar los datos.")


