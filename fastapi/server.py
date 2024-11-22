import shutil
import json
import io
from fastapi.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import pandas as pd
from typing import List, Optional
import datetime

from pydantic import BaseModel as PydanticBaseModel

class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True

class Contrato(BaseModel):
    fecha: str
    centro_seccion: str
    nreg: str
    nexp: str
    objeto: str
    tipo: str
    procedimiento: str
    numlicit: str
    numinvitcurs: str
    proc_adjud: str
    presupuesto_con_iva: str
    valor_estimado: str
    importe_adj_con_iva: str
    adjuducatario: str
    fecha_formalizacion: str
    I_G: str

class ListadoContratos(BaseModel):
    contratos = List[Contrato]

app = FastAPI(
    title="Servidor de datos",
    description="Servimos datos de contratos, pero podríamos hacer muchas otras cosas, la la la.",
    version="0.1.0",
)

@app.get("/retrieve_data/")
def retrieve_data():
    todosmisdatos = pd.read_csv('./contratos_inscritos_simplificado_2023.csv', sep=';')
    todosmisdatos = todosmisdatos.fillna(0)
    todosmisdatosdict = todosmisdatos.to_dict(orient='records')
    listado = ListadoContratos()
    listado.contratos = todosmisdatosdict
    return listado

current_id = 0  # Variable global para el ID de mascotas

def get_new_id():
    global current_id
    current_id += 1
    return current_id

current_id_duenos = 0

def get_new_id_duenos():
    global current_id_duenos
    current_id_duenos += 1
    return current_id_duenos

class FormDataDuenos(BaseModel):
    Nombre: str
    Telefono: str
    email: str

class FormDataMascota(BaseModel):
    nombre_dueño: str
    nombre_mascota: str
    tipo: str
    raza: Optional[str] = None
    edad: int
    tratamientos: Optional[str] = None
    class Config:
        orm_mode = True

class FormDataCitas(BaseModel):
    Nombre_dueño: str
    Nombre_mascota: str
    Tratamiento: str
    Nivel_urgencia: int
    Fecha_inicio: str
    Fecha_fin: str
        

file_path = "./duenos.txt"
file_path_mascotas = "./mascotas.txt"
citas_path = "./citas.txt"

@app.post("/envio/")
async def submit_form(data: FormDataDuenos):
    dueños_registrados = []
    try:
        # Leer los dueños registrados
        with open(file_path, "r") as file:
            dueños_registrados = json.load(file)
            if any(d.get('Nombre') == data.Nombre for d in dueños_registrados):
                raise HTTPException(status_code=400, detail="El dueño ya está registrado.")
    except FileNotFoundError:
        dueños_registrados = []
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error al leer el archivo de dueños.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error inesperado: {str(e)}")

    # Generar un nuevo ID para el dueño
    nuevo_id = get_new_id_duenos()
    data_dict = data.dict()
    data_dict['ID'] = nuevo_id  # Asignar el nuevo ID al dueño

    dueños_registrados.append(data_dict)
    with open(file_path, "w") as file:
        json.dump(dueños_registrados, file, indent=4)
    
    return {"message": "Formulario recibido y guardado", "data": data_dict}

@app.post("/registro_mascota/")
async def registro_mascota(mascota: FormDataMascota):
    # Ruta del archivo donde se guardarán los datos de las mascotas
    file_path_mascotas = "mascotas.txt"  # Asegúrate de que esta ruta sea correcta para tu contenedor
    file_path_duenos = "duenos.txt"  # Suponiendo que los dueños están en "dueños.txt"

    # Leer los dueños registrados
    try:
        with open(file_path_duenos, "r") as file:
            dueños_registrados = json.load(file)
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="No se encontraron dueños registrados. Por favor, registra primero un dueño.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error al leer el archivo de dueños.")

    # Verificar si el dueño está registrado
    if not any(d['Nombre'] == mascota.nombre_dueño for d in dueños_registrados):
        raise HTTPException(status_code=400, detail="El dueño no está registrado.")

    # Generar un nuevo ID para la mascota
    nuevo_id = get_new_id()  # Asegúrate de que esta función esté definida y genere un ID único

    # Crear un diccionario con los datos de la mascota
    mascota_data = {
        "ID": nuevo_id,
        "Nombre": mascota.nombre_mascota,
        "Edad": mascota.edad,
        "Tipo": mascota.tipo,
        "Raza": mascota.raza,
        "Tratamientos": mascota.tratamientos,
        "Dueño": mascota.nombre_dueño
    }

    # Guardar los datos de la mascota en el archivo
    try:
        # Leer las mascotas existentes
        try:
            with open(file_path_mascotas, "r") as file:
                mascotas_existentes = json.load(file)
        except FileNotFoundError:
            mascotas_existentes = []  # Si no existe el archivo, comenzamos con una lista vacía

        # Agregar la nueva mascota a la lista
        mascotas_existentes.append(mascota_data)

        # Escribir la lista actualizada de mascotas en el archivo
        with open(file_path_mascotas, "w") as file:
            json.dump(mascotas_existentes, file, indent=4)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al guardar los datos de la mascota: {str(e)}")

    return {"message": "Mascota registrada con éxito", "mascota": mascota_data}

# Endpoints de Citas
@app.post("/registro_cita/")
async def registro_cita(data: FormDataCitas):
    try:
        datetime.strptime(data.Fecha_inicio, "%Y-%m-%dT%H:%M:%S")
        datetime.strptime(data.Fecha_fin, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido")

    citas_registradas = []
    try:
        with open(citas_path, "r") as file:
            citas_registradas = json.load(file)
    except FileNotFoundError:
        citas_registradas = []

    citas_registradas.append(data.dict())
    with open(citas_path, "w") as file:
        json.dump(citas_registradas, file, indent=4)

    return {"message": "Cita registrada con éxito", "data": data}

@app.get("/get_citas/")
async def get_citas():
    try:
        with open(citas_path, "r") as file:
            citas = json.load(file)
        return {"citas": citas}
    except FileNotFoundError:
        return {"citas": []}
    
from pydantic import BaseModel

class BajaDueño(BaseModel):
    nombre_dueño: str

@app.post("/baja/")
async def dar_de_baja(data: BajaDueño):
    nombre_dueño = data.nombre_dueño  # Extraer el nombre del dueño del objeto recibido

    # Ruta de los archivos
    file_path_duenos = "duenos.txt"
    file_path_mascotas = "mascotas.txt"
    
    # Leer los dueños registrados
    try:
        with open(file_path_duenos, "r") as file:
            dueños_registrados = json.load(file)
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="No se encontraron dueños registrados.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error al leer el archivo de dueños.")
    
    # Filtrar los dueños que no son el que queremos dar de baja
    dueños_actualizados = [d for d in dueños_registrados if d['Nombre'] != nombre_dueño]

    # Verificar si se realizó alguna eliminación
    if len(dueños_actualizados) == len(dueños_registrados):
        raise HTTPException(status_code=404, detail="Dueño no encontrado.")
    
    # Guardar los dueños actualizados
    with open(file_path_duenos, "w") as file:
        json.dump(dueños_actualizados, file, indent=4)

    # Leer las mascotas registradas
    try:
        with open(file_path_mascotas, "r") as file:
            mascotas_registradas = json.load(file)
    except FileNotFoundError:
        mascotas_registradas = []

    # Filtrar las mascotas que no pertenecen al dueño que queremos dar de baja
    mascotas_actualizadas = [m for m in mascotas_registradas if m['Dueño'] != nombre_dueño]

    # Guardar las mascotas actualizadas
    with open(file_path_mascotas, "w") as file:
        json.dump(mascotas_actualizadas, file, indent=4)

    return {"message": f"Dueño y sus mascotas dados de baja correctamente."}