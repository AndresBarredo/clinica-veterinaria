import streamlit as st
from streamlit_calendar import calendar
import requests

st.title("Calendario y Citas 📆")

# URLs del backend
backend_registro_cita = "http://fastapi:8000/registro_cita/"
backend_get_citas = "http://fastapi:8000/get_citas/"



# Inicializar events en st.session_state si no está presente
if "events" not in st.session_state:
    st.session_state["events"] = []  # Inicializa con una lista vacía

def obtener_color(nivel_urgencia):
    colores = {
        1: "#3DD56D",  # Verde
        2: "#A3D356",  # Verde / Amarillo
        3: "#F0C048",  # Amarillo
        4: "#F59E42",  # Naranja
        5: "#FF6C6C",  # Rojo
    }
    return colores.get(nivel_urgencia, "#FFA07A")  # Color por defecto

# Función para cargar eventos desde el backend
def cargar_eventos():
    try:
        response = requests.get(backend_get_citas)
        if response.status_code == 200:
            citas = response.json().get("citas", [])
            st.session_state["events"] = []  # Reinicia la lista para evitar duplicados
            for cita in citas:
                evento = {
                    "title": f"{cita['Nombre_mascota']} - {cita['Tratamiento']}",
                    "color": obtener_color(cita["Nivel_urgencia"]),
                    "start": cita["Fecha_inicio"],
                    "end": cita["Fecha_fin"],
                    "resourceId": "a",
                }
                st.session_state["events"].append(evento)
        else:
            st.error("Error al cargar las citas desde el backend.")
    except Exception as e:
        st.error(f"Error de conexión al backend: {e}")

# Cargar eventos al inicio
cargar_eventos()

# Función para cargar dueños y mascotas
# Función para cargar dueños y mascotas desde el backend
def cargar_dueños_y_mascotas():
    url_duenos = "http://fastapi:8000/get_dueños/"
    url_mascotas = "http://fastapi:8000/get_mascotas/"

    try:
        dueños = requests.get(url_duenos).json().get("dueños", [])
        mascotas = requests.get(url_mascotas).json().get("mascotas", [])
    except Exception as e:
        st.error(f"Error al conectar con el backend: {e}")
        dueños, mascotas = [], []

    return dueños, mascotas

# Cargar dueños y mascotas
dueños, mascotas = cargar_dueños_y_mascotas()

# Función para obtener el color según el nivel de emergencia

# Función popup para registrar nueva cita
@st.dialog("Registrar nueva cita")
def popup():
    st.write("Fecha de la cita:")
    with st.form("formulario_cita"):
        nombre_dueño = st.selectbox("Nombre del Dueño", [d["Nombre"] for d in dueños])
        mascotas_dueño = [m["Nombre"] for m in mascotas if m["Dueño"] == nombre_dueño]
        nombre_mascota = st.selectbox("Nombre de la Mascota", mascotas_dueño)
        tratamiento = st.text_input("Tratamiento")
        urgencia = st.slider("Nivel de urgencia (1 - Baja, 5 - Alta)", 1, 5, 1)

        submitted = st.form_submit_button("Registrar cita")

    if submitted:
        if not st.session_state.get("time_inicial") or not st.session_state.get("time_final"):
            st.error("Seleccione un rango de tiempo válido en el calendario.")
            return

        # Crear nuevo evento con el color según nivel de emergencia
        nuevo_evento = {
            "Nombre_dueño": nombre_dueño,
            "Nombre_mascota": nombre_mascota,
            "Tratamiento": tratamiento,
            "Nivel_urgencia": urgencia,
            "Fecha_inicio": st.session_state["time_inicial"],
            "Fecha_fin": st.session_state["time_final"],
        }

        response = requests.post("http://fastapi:8000/registro_cita/", json=nuevo_evento)

        if response.status_code == 200:
            st.success("Cita registrada con éxito")
            # Añadir el evento al calendario con el color correspondiente
            evento_color = {
                "title": f"{nombre_mascota} - {tratamiento}",
                "color": obtener_color(urgencia),
                "start": st.session_state["time_inicial"],
                "end": st.session_state["time_final"],
                "resourceId": "a",
            }
            st.session_state["events"].append(evento_color)
        else:
            st.error("Error al registrar la cita")

# Configuración del calendario
calendar_options = {
    "editable": "true",
    "navLinks": "true",
    "selectable": "true",
    "initialView": "timeGridWeek",  # Cambiar a vista semanal con horarios
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "timeGridDay,timeGridWeek"
    },
    "slotMinTime": "08:00:00",  # Hora mínima
    "slotMaxTime": "20:00:00",  # Hora máxima
    "allDaySlot": False,  # Ocultar "all-day" para enfocarse en las horas
}

state = calendar(
    events=st.session_state["events"],
    options=calendar_options,
    custom_css="""
    .fc-event-past {
        opacity: 0.8;
    }
    .fc-event-time {
        font-style: italic;
    }
    .fc-event-title {
        font-weight: 700;
    }
    .fc-toolbar-title {
        font-size: 2rem;
    }
    """,
    key="calendar",
)

if state.get("select") is not None:
    st.session_state["time_inicial"] = state["select"]["start"]
    st.session_state["time_final"] = state["select"]["end"]
    popup()
