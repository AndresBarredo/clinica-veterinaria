import streamlit as st
import requests

# URL del microservicio FastAPI
url_mascota = "http://fastapi:8000/registro_mascota/"

st.title("Registro de Mascotas en la Clínica Veterinaria")

# Crear el formulario
with st.form("registro_mascota"):
    nombre = st.text_input("Nombre de la Mascota")
    edad = st.number_input("Edad de la Mascota", min_value=0, step=1)
    tipo = st.selectbox("Tipo", [("Perro", 0), ("Gato", 1)], format_func=lambda x: x[0])[1]
    dueño = st.text_input("Nombre del Dueño")

    submit_button = st.form_submit_button(label="Registrar Mascota")

if submit_button:
    # Crear el payload con los datos del formulario
    payload = {
        "nombre": nombre,
        "edad": edad,
        "tipo": tipo,
        "dueño": dueño
    }

    # Enviar los datos al microservicio FastAPI
    response = requests.post(url_mascota, json=payload)

    # Mostrar el resultado de la solicitud
    if response.status_code == 200:
        st.success("Mascota registrada correctamente")
        st.json(response.json())
    else:
        st.error("Error al registrar la mascota")