import streamlit as st

from streamlit_calendar import calendar

import requests


st.title("Demo de streamlit-calendar con popup para inserción de datos 📆")


def send(data):
    #r = requests.post(
    #    backend, json=data
    #)
    #return r.status_code
    return '200'
@st.dialog("Mete info!")
def popup ():
    st.write(f'Fecha de la cita')
    with st.form("my_form"):
        tratamiento = st.text_input("Ingrese el tratamiento:")
        #edificio = ,,,
        #
        submitted = st.form_submit_button("Submit form")

    if submitted:
        envio = send(...)
        if envio == '200':
            st.success("Enviado con éxito, puede cerrar!")
        else:
            st.error("No se envio, status_code: {}".format(envio))


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
calendar_resources = [
    {"id": "a", "building": "Clinica 1", "title": "Consulta A"},
    {"id": "b", "building": "Clinica 1", "title": "Consulta A"},
    {"id": "c", "building": "Clinica 1", "title": "Consulta B"},
    {"id": "d", "building": "Clinica 1", "title": "Consulta B"},
    {"id": "e", "building": "Clinica 1", "title": "Consulta A"},
    {"id": "f", "building": "Clinica 1", "title": "Consulta B"},
]


backend = "http://fastapi:8000/citas"  # Esta URL meterla en un parámetro de configuración


fecha = ''


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
    events=st.session_state.get("events", events),
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

name = ''
if state.get("eventsSet") is not None:
    st.session_state["events"] = state["eventsSet"]
    #st.session_state["fecha"] = state["date"]

if state.get('select') is not None:
    st.session_state["time_inicial"] = state["select"]["start"]
    st.session_state["time_final"] = state["select"]["end"]
    popup()

if state.get('eventChange') is not None:
    data = state.get('eventChange').get('event')
    ## aquí haríamos un requests.post()

    st.success('cita camboada con éxito')

if st.session_state.get("fecha") is not None:
    st.write('fecha')
    #st.write(st.session_state["fecha"])
   # with st.popover("Open popover"):
   #     st.markdown("Hello World 👋")
   #     name = st.text_input("What's your name?")



