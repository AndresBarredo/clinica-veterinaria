import streamlit as st
import requests
from datetime import datetime

API_URL = "http://fastapi:8000"

# Obtener dueños
response_dueños = requests.get(f"{API_URL}/get_dueños/")
if response_dueños.status_code == 200:
    dueños = response_dueños.json().get("dueños", [])
    nombres_dueños = [d['Nombre'] for d in dueños]
    print(f"Nombres de dueños: {nombres_dueños}")  # Debug log
else:
    st.error("Error al obtener dueños")
    nombres_dueños = []

# Obtener mascotas
response_mascotas = requests.get(f"{API_URL}/get_mascotas/")
if response_mascotas.status_code == 200:
    mascotas = response_mascotas.json().get("mascotas", [])
    nombres_mascotas = [m['nombre_mascota'] for m in mascotas]
    print(f"Nombres de mascotas: {nombres_mascotas}")  # Debug log
else:
    st.error("Error al obtener mascotas")
    nombres_mascotas = []

# Interfaz de usuario
st.title("Generar Factura")

nombre_dueño = st.selectbox("Selecciona el dueño:", nombres_dueños)
nombre_mascota = st.selectbox("Selecciona la mascota:", nombres_mascotas)
tratamiento = st.text_input("Tratamiento:")
precio = st.number_input("Precio:", min_value=0.0)

if st.button("Generar Factura"):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    factura_data = {
        "nombre_dueño": nombre_dueño,
        "nombre_mascota": nombre_mascota,
        "tratamiento": tratamiento,
        "precio": precio,
        "fecha": fecha
    }
    response = requests.post(f"{API_URL}/generar_factura/", json=factura_data)
    
    if response.status_code == 200:
        st.success("Factura generada con éxito")
        st.write("Factura:")
        st.write(f"Dueño: {nombre_dueño}")
        st.write(f"Mascota: {nombre_mascota}")
        st.write(f"Tratamiento: {tratamiento}")
        st.write(f"Precio: ${precio:.2f}")
        st.write(f"Fecha: {fecha}")
    else:
        st.error("Error al generar factura")
    