import shutil
import json
import io
from fastapi.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import pandas as pd
from typing import List, Optional

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

file_path = "./duenos.txt"

@app.post("/envio/")
async def submit_form(data: FormDataDuenos):
    dueños_registrados = []
    try:
        with open(file_path, "r") as file:
            dueños_registrados = json.load(file)
            if any(d.get('Nombre') == data.Nombre for d in dueños_registrados):
                raise HTTPException(status_code=400, detail="El dueño ya está registrado.")
    except FileNotFoundError:
        dueños_registrados = []
    except HTTPException as e:
        raise HTTPException(status_code=500, detail="Error en el registro.") from e
    finally:
        dueños_registrados.append(data.dict())
        with open(file_path, "w") as file:
            json.dump(dueños_registrados, file, indent=4)
        return {"message": "Formulario recibido y guardado", "data": data}

@app.post("/registro_mascota/")
async def registro_mascota(mascota: FormDataMascota):
    try:
        # Leer los dueños registrados
        with open(file_path, "r") as file:
            dueños_registrados = json.load(file)
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="No se encontraron dueños registrados. Por favor, registra primero un dueño.")
    
    # Verificar si el dueño está registrado
    if not any(d['Nombre'] == mascota.nombre_dueño for d in dueños_registrados):
        raise HTTPException(status_code=400, detail="El dueño no está registrado.")
    
    # Crear un diccionario con los datos de la mascota
    mascota_data = {
        "ID": get_new_id(),
        "Nombre": mascota.nombre_mascota,
        "Edad": mascota.edad,
        "Tipo": mascota.tipo,
        "Raza": mascota.raza,
        "Tratamientos": mascota.tratamientos,
        "Dueño": mascota.nombre_dueño
    }

    return {"message": "Mascota registrada con éxito", "mascota": mascota_data}


