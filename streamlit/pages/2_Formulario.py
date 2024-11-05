import streamlit as st
import requests
from datetime import datetime

# URL del microservicio FastAPI
url = "http://fastapi:8000/envio/"

st.title("Registrar Dueños 🐶")

# Crear el formulario
with st.form("envio"):
    nombre = st.text_input("Nombre")
    telefono = st.text_input("Teléfono")
    email = st.text_input("Email")

    submit_button = st.form_submit_button(label="Enviar")

    # Crear el payload para enviar al microservicio
    payload = {
        "Nombre": nombre,
        "Telefono": telefono,
        "email": email,
    }

    # Enviar los datos al microservicio usando requests
    response = requests.post(url, json=payload)

# Mostrar el resultado de la solicitud
if response.status_code == 200:
    st.success("Datos enviados correctamente")
    st.json(response.json())
else:
    st.error(f"Error al enviar los datos: {response.status_code}")
    st.write(response.text)  # Mostrar el mensaje de error detallado
