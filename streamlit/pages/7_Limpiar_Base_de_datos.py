import streamlit as st
import requests

st.title("Limpiar Base de Datos 🗑️")

# Inicializar la variable de estado si no existe
if 'confirmar_limpieza' not in st.session_state:
    st.session_state.confirmar_limpieza = False

st.warning("⚠️ Esta acción eliminará TODOS los datos de la base de datos. Esta acción no se puede deshacer.")

# Primer botón
if not st.session_state.confirmar_limpieza:
    if st.button("Limpiar Base de Datos"):
        st.session_state.confirmar_limpieza = True
        st.experimental_rerun()

# Segundo botón (confirmación)
if st.session_state.confirmar_limpieza:
    st.warning("🚨 ¿Estás realmente seguro? Esta acción eliminará todos los datos permanentemente.")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Sí, eliminar todos los datos"):
            response = requests.delete("http://fastapi:8000/limpiar_base_datos")
            if response.status_code == 200:
                st.success("✅ Base de datos limpiada exitosamente")
                st.balloons()
                # Resetear el estado
                st.session_state.confirmar_limpieza = False
            else:
                st.error(f"❌ Error al limpiar la base de datos: {response.text}")
    
    with col2:
        if st.button("Cancelar"):
            st.session_state.confirmar_limpieza = False
            st.experimental_rerun()
