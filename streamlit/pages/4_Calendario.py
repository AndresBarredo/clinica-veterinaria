import streamlit as st
from streamlit_calendar import calendar
import requests

# URLs del backend
backend_registro_cita = "http://fastapi:8000/registro_cita/"
backend_get_citas = "http://fastapi:8000/get_citas/"

st.title("Calendario y Citas 📆")

# Botón para limpiar citas
if st.button("Limpiar todas las citas"):
    try:
        response = requests.delete(f"{backend_registro_cita.replace('/registro_cita/', '/limpiar_citas')}")
        if response.status_code == 200:
            st.success("Todas las citas han sido eliminadas")
            # Limpiar los eventos en la sesión
            st.session_state["events"] = []
            # Forzar la actualización de la página
            st.rerun()
        else:
            st.error("Error al limpiar las citas")
    except Exception as e:
        st.error(f"Error de conexión: {str(e)}")

# Inicializar events en st.session_state si no está presente
if "events" not in st.session_state:
    st.session_state["events"] = []

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

# Función para cargar dueños y mascotas desde el backend
def cargar_dueños_y_mascotas():
    url_duenos = "http://fastapi:8000/duenos"
    url_mascotas = "http://fastapi:8000/mascotas"

    try:
        response_duenos = requests.get(url_duenos)
        response_mascotas = requests.get(url_mascotas)
        
        print(f"Respuesta dueños: {response_duenos.text}")  # Debug log
        print(f"Respuesta mascotas: {response_mascotas.text}")  # Debug log
        
        if response_duenos.status_code == 200 and response_mascotas.status_code == 200:
            dueños = response_duenos.json().get("duenos", [])
            mascotas = response_mascotas.json().get("mascotas", [])
            
            print(f"Dueños cargados: {dueños}")  # Debug log
            print(f"Mascotas cargadas: {mascotas}")  # Debug log
            
            return dueños, mascotas
        else:
            st.error("Error al obtener datos del servidor")
            return [], []
    except Exception as e:
        st.error(f"Error al conectar con el backend: {e}")
        print(f"Error detallado: {str(e)}")  # Debug log
        return [], []

# Cargar dueños y mascotas
dueños, mascotas = cargar_dueños_y_mascotas()

# Función para obtener el color según el nivel de emergencia

# Función popup para registrar nueva cita
@st.dialog("Registrar nueva cita")
def popup():
    st.write("Fecha de la cita:")
    with st.form("formulario_cita"):
        # Obtener la lista de dueños
        dueños, mascotas = cargar_dueños_y_mascotas()
        
        if not dueños:
            st.error("No hay dueños registrados")
            return
            
        nombre_dueño = st.selectbox(
            "Nombre del Dueño",
            options=[d["Nombre"] for d in dueños if d.get("Nombre")]
        )
        
        # Filtrar mascotas por dueño
        mascotas_dueño = [
            m["nombre_mascota"] 
            for m in mascotas 
            if m.get("nombre_dueño") == nombre_dueño
        ]
        
        if not mascotas_dueño:
            st.warning(f"No hay mascotas registradas para {nombre_dueño}")
            
        nombre_mascota = st.selectbox(
            "Nombre de la Mascota",
            options=mascotas_dueño if mascotas_dueño else ["No hay mascotas disponibles"]
        )
        
        tratamiento = st.text_input("Tratamiento")
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
            "Fecha_inicio": st.session_state["time_inicial"],
            "Fecha_fin": st.session_state["time_final"],
        }

        response = requests.post(backend_registro_cita, json=nuevo_evento)

        if response.status_code == 200:
            st.success("Cita registrada con éxito")
            
            # Actualizar eventos inmediatamente
            cargar_eventos()
            
            # Forzar la actualización de la página usando st.rerun()
            st.rerun()
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
