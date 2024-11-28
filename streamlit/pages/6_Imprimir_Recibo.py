import streamlit as st
import requests
from datetime import datetime

API_URL = "http://fastapi:8000"

# Obtener dueños
dueños = requests.get(f"{API_URL}/get_dueños/").json()  # Usa la ruta correcta
nombres_dueños = [d['Nombre'] for d in dueños.get("dueños", [])]

# Obtener mascotas
mascotas = requests.get(f"{API_URL}/get_mascotas/").json()  # Usa la ruta correcta
nombres_mascotas = [m['Nombre'] for m in mascotas.get("mascotas", [])]

# Obtener citas
citas = requests.get(f"{API_URL}/get_citas/").json()  # Usa la ruta correcta

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
    st.success(response.json())
    
    st.write("Factura:")
    st.write(f"Dueño: {nombre_dueño}")
    st.write(f"Mascota: {nombre_mascota}")
    st.write(f"Tratamiento: {tratamiento}")
    st.write(f"Precio: ${precio:.2f}")
    st.write(f"Fecha: {fecha}")
    