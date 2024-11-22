import streamlit as st
import requests

# URL del microservicio FastAPI
url = "http://fastapi:8000/baja/"

st.title("Dar de Baja a Dueños y Mascotas 🚫")

# Crear el formulario para dar de baja
with st.form("dar_de_baja"):
    nombre_dueño = st.text_input("Nombre del Dueño a dar de baja")

    submit_button = st.form_submit_button(label="Dar de Baja")

    if submit_button:
        # Crear el payload para enviar al microservicio
        payload = {
            "nombre_dueño": nombre_dueño,
        }

        # Enviar los datos al microservicio usando requests
        response = requests.post(url, json=payload)

        # Mostrar el resultado de la solicitud
        if response.status_code == 200:
            st.success("Dueño y sus mascotas dados de baja correctamente.")
        else:
            st.error(f"Error al dar de baja: {response.status_code}")
            st.write(response.text)  # Mostrar el mensaje de error detallado