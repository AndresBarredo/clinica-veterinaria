import streamlit as st
from streamlit_calendar import calendar
import requests

st.title("Calendario📆 de polllo")

# URLs del backend
backend_registro_cita = "http://fastapi:8000/registro_cita/"
backend_get_citas = "http://fastapi:8000/get_citas/"

# Define events antes de cualquier referencia
events = [
    {
        "title": "Consulta Perrito",
        "color": "#FF6C6C",
        "start": "2023-07-03",
        "end": "2023-07-05",
        "resourceId": "a",
    },
    {
        "title": "Consulta Gatito ",
        "color": "#FFBD45",
        "start": "2023-07-01",
        "end": "2023-07-10",
        "resourceId": "b",
    },
    {
        "title": "Consulta Perrito",
        "color": "#FF4B4B",
        "start": "2023-07-20",
        "end": "2023-07-20",
        "resourceId": "c",
    },
    {
        "title": "Consulta Gatito",
        "color": "#FF6C6C",
        "start": "2023-07-23",
        "end": "2023-07-25",
        "resourceId": "d",
    },
    {
        "title": "Consulta Loro",
        "color": "#FFBD45",
        "start": "2023-07-29",
        "end": "2023-07-30",
        "resourceId": "e",
    },
    {
        "title": "Consulta Guacamayo Ibérico",
        "color": "#FF4B4B",
        "start": "2023-07-28",
        "end": "2023-07-20",
        "resourceId": "f",
    },
    {
        "title": "Estudio",
        "color": "#FF4B4B",
        "start": "2023-07-01T08:30:00",
        "end": "2023-07-01T10:30:00",
        "resourceId": "a",
    },
    {
        "title": "Recados",
        "color": "#3D9DF3",
        "start": "2023-07-01T07:30:00",
        "end": "2023-07-01T10:30:00",
        "resourceId": "b",
    },
    {
        "title": "Revisión Perrito",
        "color": "#3DD56D",
        "start": "2023-07-02T10:40:00",
        "end": "2023-07-02T12:30:00",
        "resourceId": "c",
    },
]

# Inicializar events en st.session_state si no está presente o está mal inicializado
if "events" not in st.session_state or not isinstance(st.session_state["events"], list):
    st.session_state["events"] = events  # Inicializa con la lista predeterminada

# Función para cargar eventos desde el backend
def cargar_eventos():
    response = requests.get(backend_get_citas)
    if response.status_code == 200:
        citas = response.json().get("citas", [])
        st.session_state["events"] = []  # Reinicia la lista para evitar duplicados
        for cita in citas:
            evento = {
                "title": f"{cita['Nombre_mascota']} - {cita['Tratamiento']}",
                "color": "#FFA07A",
                "start": cita["Fecha_inicio"],
                "end": cita["Fecha_fin"],
                "resourceId": "a",
            }
            st.session_state["events"].append(evento)

# Cargar eventos al inicio
cargar_eventos()

# Función para registrar una cita en el backend
def send(data):
    response = requests.post(backend_registro_cita, json=data)
    return response.status_code

# Función popup para registrar nueva cita
@st.dialog("Registrar nueva cita")
def popup():
    st.write("Fecha de la cita:")
    with st.form("formulario_cita"):
        nombre_dueño = st.text_input("Nombre del dueño:")
        nombre_mascota = st.text_input("Nombre de la mascota:")
        tipo_animal = st.selectbox("Tipo de animal:", ["Perro", "Gato", "Loro", "Otro"])
        tratamiento = st.text_input("Tratamiento:")
        urgencia = st.slider("Nivel de urgencia (1 - Baja, 5 - Alta)", 1, 5, 1)

        submitted = st.form_submit_button("Registrar cita")

    if submitted:
        if not st.session_state.get("time_inicial") or not st.session_state.get("time_final"):
            st.error("Seleccione un rango de tiempo válido en el calendario.")
            return

        nuevo_evento = {
            "Nombre_dueño": nombre_dueño,
            "Nombre_mascota": nombre_mascota,
            "Tratamiento": tratamiento,
            "Nivel_urgencia": urgencia,
            "Fecha_inicio": st.session_state.get("time_inicial"),
            "Fecha_fin": st.session_state.get("time_final"),
        }

        response = requests.post(backend_registro_cita, json=nuevo_evento)

        if response.status_code == 200:
            st.success("Cita registrada con éxito")
            cargar_eventos()  # Recargar eventos desde el backend
        else:
            st.error("Error al registrar la cita")

# Configuración del calendario
mode = st.selectbox(
    "Calendar Mode:",
    (
        "daygrid",
        "timegrid",
        "timeline",
        "resource-daygrid",
        "resource-timegrid",
        "resource-timeline",
        "list",
        "multimonth",
    ),
)

calendar_resources = [
    {"id": "a", "building": "Clinica 1", "title": "Consulta A"},
    {"id": "b", "building": "Clinica 1", "title": "Consulta A"},
    {"id": "c", "building": "Clinica 1", "title": "Consulta B"},
    {"id": "d", "building": "Clinica 1", "title": "Consulta B"},
    {"id": "e", "building": "Clinica 1", "title": "Consulta A"},
    {"id": "f", "building": "Clinica 1", "title": "Consulta B"},
]

calendar_options = {
    "editable": "true",
    "navLinks": "true",
    "resources": calendar_resources,
    "selectable": "true",
}
calendar_options = {
    **calendar_options,
    "initialDate": "2023-07-01",
    "initialView": "resourceTimeGridDay",
    "resourceGroupField": "building",
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
    key='timegrid',
)

if state.get("eventsSet") is not None:
    st.session_state["events"] = state["eventsSet"]

if state.get('select') is not None:
    st.session_state["time_inicial"] = state["select"]["start"]
    st.session_state["time_final"] = state["select"]["end"]
    popup()

if state.get('eventChange') is not None:
    data = state.get('eventChange').get('event')
    st.success('Cita cambiada con éxito')

if st.session_state.get("fecha") is not None:
    st.write('Fecha seleccionada')