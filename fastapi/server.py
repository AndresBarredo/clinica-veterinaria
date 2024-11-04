import shutil

import json
import io
from fastapi.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile,Form
import pandas as pd
from typing import  List

from pydantic import BaseModel as PydanticBaseModel

class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True

class Contrato(BaseModel):
    #titulo:str
    #autor:str
    #pais:str
    #genero:str
    fecha:str
    centro_seccion:str
    nreg:str
    nexp:str
    objeto:str
    tipo:str
    procedimiento:str
    numlicit:str
    numinvitcurs:str
    proc_adjud:str
    presupuesto_con_iva:str
    valor_estimado:str
    importe_adj_con_iva:str
    adjuducatario:str
    fecha_formalizacion:str
    I_G:str


class ListadoContratos(BaseModel):
    contratos = List[Contrato]

app = FastAPI(
    title="Servidor de datos",
    description="""Servimos datos de contratos, pero podríamos hacer muchas otras cosas, la la la.""",
    version="0.1.0",
)


@app.get("/retrieve_data/")
def retrieve_data ():
    todosmisdatos = pd.read_csv('./contratos_inscritos_simplificado_2023.csv',sep=';')
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

class FormDataDuenos(BaseModel):
    Nombre: str
    Telefono: str
    email: str
    
class FormDataMascota(BaseModel):
    ID: int  # Este será un valor auto-incremental que gestionaremos.
    Nombre: str
    Edad: int
    Tipo: int  # 0 para perro, 1 para gato
    Dueño: str  # Nombre del dueño ya registrado

    class Config:
        orm_mode = True

file_path = "sqlalchemy/duenos.txt"

@app.post("/envio/")
async def submit_form(data: FormDataDuenos):
    # Cargar dueños existentes
    try:
        with open(file_path, "r") as file:
            duenos = json.load(file)
    except FileNotFoundError:
        duenos = []  # Si no existe, inicializa una lista vacía

    # Añadir el nuevo dueño al listado
    duenos.append(data.dict())  # Convertir el modelo a diccionario y añadirlo a la lista

    # Guardar la lista actualizada en el archivo
    with open(file_path, "w") as file:
        json.dump(duenos, file, indent=4)  # Guarda con formato JSON legible
        print("Datos guardados en duenos.txt")  # Mensaje de confirmación

    return {"message": "Formulario recibido y guardado", "data": data}

# Lista temporal de dueños registrados
# Ejemplo: [{'Nombre': 'Carlos', 'Telefono': '123456789', 'email': 'carlos@example.com'}]
dueños_registrados = [{"Nombre": "Carlos", "Telefono": "123456789", "email": "carlos@example.com"}]

@app.post("/registro_mascota/")
async def registro_mascota(nombre: str, edad: int, tipo: int, dueño: str):
    # Validar que el dueño esté registrado
    if not any(d['Nombre'] == dueño for d in dueños_registrados):
        return JSONResponse(status_code=400, content={"error": "El dueño no está registrado."})

    # Crear una nueva mascota con un ID auto-incremental
    mascota = FormDataMascota(
        ID=get_new_id(),
        Nombre=nombre,
        Edad=edad,
        Tipo=tipo,
        Dueño=dueño
    )
    # Aquí podrías añadir la mascota a una base de datos o lista de almacenamiento

    return {"message": "Mascota registrada con éxito", "mascota": mascota}
