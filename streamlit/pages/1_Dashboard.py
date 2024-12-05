import streamlit as st
import requests
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt

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

    # Crear las gráficas a partir de las estadísticas
    st.header("📊 Análisis Gráfico")

    # Gráfica: Dueños vs Ingresos
    if "nombres_dueños" in estadisticas and "ingresos_por_dueño" in estadisticas:
        nombres_dueños = estadisticas["nombres_dueños"]
        ingresos_dueños = estadisticas["ingresos_por_dueño"]

        # Crear los datos para la gráfica
        data_dueños = {
            "Dueños": nombres_dueños,
            "Ingresos": ingresos_dueños,
        }

        fig, ax = plt.subplots(figsize=(10, 6))

        # Configurar el fondo
        fig.patch.set_facecolor('lightgreen')
        ax.set_facecolor('lightgreen')

        # Crear las barras
        ax.bar(data_dueños["Dueños"], data_dueños["Ingresos"], color='skyblue', edgecolor='black')

        # Añadir etiquetas y título
        ax.set_title('🐶 Dueños vs 💸 Ingresos Totales', fontsize=16, weight='bold')
        ax.set_xlabel('Dueños', fontsize=12)
        ax.set_ylabel('Ingresos Totales (€)', fontsize=12)
        ax.tick_params(axis='x', rotation=45, labelsize=10)  # Rotar etiquetas de nombres
        ax.tick_params(axis='y', labelsize=10)

        # Ajustar ticks y estilos
        plt.grid(axis='y', linestyle='--', linewidth=0.5)

        # Mostrar la gráfica en el Dashboard
        st.pyplot(fig)

    else:
        st.error("No se pudieron cargar las estadísticas. Presiona el botón para reintentar.")
else:
    # Mostrar mensaje inicial o por defecto
    st.info("Presiona el botón 'Actualizar Estadísticas' para cargar los datos.")
