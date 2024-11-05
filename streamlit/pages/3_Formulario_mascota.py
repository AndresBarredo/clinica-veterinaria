import streamlit as st
import requests

# URL del microservicio FastAPI
url = "http://fastapi:8000/registro_mascota/"

st.title("Registrar Mascota 🐾")

# Crear el formulario para registrar la mascota
with st.form("registro_mascota"):
    nombre_mascota = st.text_input("Nombre de la Mascota")
    tipo = st.selectbox("Tipo de Mascota", ["Perro", "Gato"])
    raza = st.text_input("Raza")
    edad = st.number_input("Edad", min_value=0, max_value=50, step=1)
    tratamientos = st.text_area("Tratamientos (describa los tratamientos que ha recibido)")

    submit_button = st.form_submit_button(label="Registrar Mascota")

    # Crear el payload para enviar al microservicio
    payload = {
        "nombre_mascota": nombre_mascota,
        "tipo": tipo,
        "raza": raza,
        "edad": edad,
        "tratamientos": tratamientos,
    }

    # Enviar los datos al microservicio usando requests si se presiona el botón
    if submit_button:
        response = requests.post(url, json=payload)

        # Mostrar el resultado de la solicitud
        if response.status_code == 200:
            st.success("Datos de la mascota enviados correctamente")
            st.json(response.json())
        else:
            st.error("Error al enviar los datos")
