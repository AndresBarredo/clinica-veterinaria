import shutil
import json
from fastapi.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import pandas as pd
from typing import List, Optional
from pydantic import BaseModel as PydanticBaseModel, validator
from basededatos import BaseDeDatos

class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True

# Modelos de datos
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
    contratos: List[Contrato]

class FormDataDuenos(BaseModel):
    Nombre: str
    Telefono: str
    email: str

    @validator('Nombre')
    def nombre_no_vacio(cls, v):
        if not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip()

    @validator('Telefono')
    def telefono_valido(cls, v):
        if not v.strip():
            raise ValueError('El teléfono no puede estar vacío')
        return v.strip()

    @validator('email')
    def email_valido(cls, v):
        if not v.strip():
            raise ValueError('El email no puede estar vacío')
        if '@' not in v:
            raise ValueError('Email inválido')
        return v.strip().lower()

class FormDataMascota(BaseModel):
    nombre_dueño: str
    nombre_mascota: str
    tipo: str
    raza: Optional[str] = None
    edad: int
    tratamientos: Optional[str] = None

class FormDataCitas(BaseModel):
    Nombre_dueño: str
    Nombre_mascota: str
    Tratamiento: str
    Nivel_urgencia: int
    Fecha_inicio: str
    Fecha_fin: str

class Factura(BaseModel):
    nombre_dueño: str
    nombre_mascota: str
    tratamiento: str
    precio: float
    fecha: str

class BajaDueño(BaseModel):
    nombre_dueño: str

# Inicialización de la aplicación
app = FastAPI(
    title="Servidor de datos",
    description="Servimos datos de contratos, pero podríamos hacer muchas otras cosas.",
    version="0.1.0",
)
db = BaseDeDatos()

# Definición de rutas para archivos
file_path = "./duenos.txt"
file_path_mascotas = "./mascotas.txt"
citas_path = "./citas.txt"
facturas_path = "./facturas.txt"

# Funciones auxiliares
def load_data(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_data(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

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

# Endpoints
@app.get("/retrieve_data/")
def retrieve_data():
    todosmisdatos = pd.read_csv('./contratos_inscritos_simplificado_2023.csv', sep=';')
    todosmisdatos = todosmisdatos.fillna(0)
    todosmisdatosdict = todosmisdatos.to_dict(orient='records')
    listado = ListadoContratos()
    listado.contratos = todosmisdatosdict
    return listado

@app.get("/estadisticas/")
async def obtener_estadisticas():
    return await db.obtener_estadisticas()

@app.post("/envio/")
async def submit_form(data: FormDataDuenos):
    try:
        print(f"Datos recibidos: {data.dict()}")  # Log para ver qué datos llegan
        
        # Verificar si el dueño ya existe
        dueno_existente = await db.buscar_dueno(data.Nombre)
        if dueno_existente:
            print(f"Dueño ya existe: {dueno_existente}")  # Log para depuración
            raise HTTPException(status_code=400, detail="El dueño ya está registrado.")

        # Crear nuevo dueño
        nuevo_dueno = data.dict()
        print(f"Intentando crear dueño: {nuevo_dueno}")  # Log para depuración
        resultado = await db.crear_dueno(nuevo_dueno)
        print(f"Resultado de crear dueño: {resultado}")  # Log del resultado
        return {"message": "Formulario recibido y guardado", "data": resultado}
    except HTTPException as he:
        print(f"Error de validación: {he.detail}")  # Log de errores de validación
        raise he
    except Exception as e:
        print(f"Error inesperado: {str(e)}")  # Log de errores inesperados
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/registro_mascota/")
async def crear_mascota(mascota: dict):
    try:
        # Validar que los campos requeridos estén presentes y no estén vacíos
        campos_requeridos = ["nombre_mascota", "nombre_dueño", "tipo", "edad"]
        for campo in campos_requeridos:
            if campo not in mascota or not str(mascota[campo]).strip():
                raise HTTPException(
                    status_code=400, 
                    detail=f"El campo {campo} es requerido y no puede estar vacío"
                )
        
        # Limpiar datos antes de enviarlos a la base de datos
        mascota_limpia = {
            "nombre_mascota": mascota["nombre_mascota"].strip(),
            "nombre_dueño": mascota["nombre_dueño"].strip(),
            "tipo": mascota["tipo"].strip(),
            "edad": mascota["edad"],
            "raza": mascota.get("raza", "").strip(),
            "tratamientos": mascota.get("tratamientos", "").strip()
        }
        
        resultado = await db.crear_mascota(mascota_limpia)
        return resultado
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/registro_cita/")
async def registro_cita(data: FormDataCitas):
    try:
        print(f"Datos de cita recibidos: {data.dict()}")  # Debug log
        
        # Verificar que el dueño existe
        dueno = await db.buscar_dueno(data.Nombre_dueño)
        if not dueno:
            raise HTTPException(status_code=400, detail="El dueño no existe")
        
        # Verificar que la mascota existe y pertenece al dueño
        mascotas = await db.obtener_mascotas_por_dueno(data.Nombre_dueño)
        mascota_valida = any(m["Nombre"] == data.Nombre_mascota for m in mascotas)
        if not mascota_valida:
            raise HTTPException(
                status_code=400, 
                detail="La mascota no está registrada para este dueño"
            )
        
        # Guardar la cita en la base de datos con los nombres de campos correctos
        nueva_cita = {
            "Nombre_dueño": data.Nombre_dueño,
            "Nombre_mascota": data.Nombre_mascota,
            "Tratamiento": data.Tratamiento,
            "Nivel_urgencia": data.Nivel_urgencia,
            "Fecha_inicio": data.Fecha_inicio,
            "Fecha_fin": data.Fecha_fin
        }
        
        resultado = await db.crear_cita(nueva_cita)
        print(f"Cita registrada: {resultado}")  # Debug log
        
        return {"message": "Cita registrada con éxito", "data": resultado}
        
    except HTTPException as he:
        print(f"Error de validación: {he.detail}")  # Debug log
        raise he
    except Exception as e:
        print(f"Error inesperado: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/duenos")
async def get_duenos():
    try:
        duenos = await db.obtener_duenos()
        print(f"Dueños obtenidos: {duenos}")  # Debug log
        return {"duenos": duenos}
    except Exception as e:
        print(f"Error al obtener dueños: {e}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mascotas")
async def get_mascotas():
    try:
        mascotas = await db.obtener_mascotas()
        print(f"Mascotas obtenidas: {mascotas}")  # Debug log
        return {"mascotas": mascotas}
    except Exception as e:
        print(f"Error al obtener mascotas: {e}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mascotas_por_dueno/{nombre_dueno}")
async def get_mascotas_por_dueno(nombre_dueno: str):
    try:
        mascotas = await db.obtener_mascotas_por_dueno(nombre_dueno)
        print(f"Mascotas obtenidas para {nombre_dueno}: {mascotas}")  # Debug log
        return {"mascotas": mascotas}
    except Exception as e:
        print(f"Error al obtener mascotas: {e}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_citas/")
async def get_citas():
    try:
        citas = await db.obtener_citas()
        print(f"Citas recuperadas: {citas}")  # Debug log
        return {"citas": citas}
    except Exception as e:
        print(f"Error al obtener citas: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/baja/")
async def dar_de_baja(dueno_data: dict):
    try:
        nombre_dueño = dueno_data.get("nombre_dueño")
        print(f"Intentando dar de baja al dueño: {nombre_dueño}")  # Debug log
        
        # Eliminar al dueño
        dueño_eliminado = await db.eliminar_dueno(nombre_dueño)
        print(f"Dueño eliminado: {dueño_eliminado}")  # Debug log
        
        # Eliminar las mascotas asociadas al dueño
        mascotas_eliminadas = await db.eliminar_mascotas_por_dueno(nombre_dueño)
        print(f"Mascotas eliminadas: {mascotas_eliminadas}")  # Debug log
        
        if dueño_eliminado and mascotas_eliminadas:
            return {"message": "Dueño y sus mascotas dados de baja correctamente."}
        else:
            raise HTTPException(status_code=404, detail="Dueño no encontrado o error al eliminar")
    except Exception as e:
        print(f"Error al dar de baja: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generar_factura/")
async def generar_factura(factura_data: dict):
    try:
        resultado = await db.crear_factura(factura_data)
        return {"message": "Factura generada con éxito", "factura": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/database")
async def debug_database():
    try:
        duenos = await db.obtener_duenos()
        mascotas = await db.obtener_mascotas()
        return {
            "duenos": duenos,
            "mascotas": mascotas,
            "total_duenos": len(duenos),
            "total_mascotas": len(mascotas)
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/duenos/")
async def crear_dueno(dueno: dict):
    try:
        # Normalizar el formato del nombre
        if "Nombre" in dueno:
            dueno["Nombre"] = dueno["Nombre"].strip()
        print(f"Creando dueño: {dueno}")  # Log para depuración
        return await db.crear_dueno(dueno)
    except Exception as e:
        print(f"Error al crear dueño: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/all")
async def debug_all():
    try:
        duenos = await db.obtener_duenos()
        mascotas = await db.obtener_mascotas()
        return {
            "duenos_raw": list(db.db.mascotas.distinct('nombre_dueño')),
            "duenos_processed": duenos,
            "mascotas_raw": list(db.db.mascotas.find({}, {'_id': 0})),
            "mascotas_processed": mascotas
        }
    except Exception as e:
        return {"error": str(e)}

@app.delete("/limpiar_base_datos")
async def limpiar_base_datos():
    try:
        print("Recibida solicitud para limpiar la base de datos")  # Debug log
        resultado = await db.limpiar_base_datos()
        
        if resultado:
            print("Base de datos limpiada exitosamente")  # Debug log
            return JSONResponse(
                status_code=200,
                content={"message": "Base de datos limpiada exitosamente"}
            )
        else:
            print("Error al limpiar la base de datos")  # Debug log
            raise HTTPException(status_code=500, detail="Error al limpiar la base de datos")
            
    except Exception as e:
        print(f"Error durante la limpieza: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=500,
            detail=f"Error al limpiar la base de datos: {str(e)}"
        )

@app.get("/get_dueños/")
async def get_dueños():
    try:
        dueños = await db.obtener_duenos()
        print(f"Dueños recuperados: {dueños}")  # Debug log
        return {"dueños": dueños}
    except Exception as e:
        print(f"Error al obtener dueños: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_mascotas/")
async def get_mascotas():
    try:
        mascotas = await db.obtener_mascotas()
        print(f"Mascotas recuperadas: {mascotas}")  # Debug log
        return {"mascotas": mascotas}
    except Exception as e:
        print(f"Error al obtener mascotas: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/limpiar_citas")
async def limpiar_citas():
    try:
        print("Recibida solicitud para limpiar las citas")  # Debug log
        resultado = await db.limpiar_citas()
        
        if resultado:
            print("Citas limpiadas exitosamente")  # Debug log
            return JSONResponse(
                status_code=200,
                content={"message": "Citas limpiadas exitosamente"}
            )
        else:
            print("Error al limpiar las citas")  # Debug log
            raise HTTPException(status_code=500, detail="Error al limpiar las citas")
            
    except Exception as e:
        print(f"Error durante la limpieza de citas: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=500,
            detail=f"Error al limpiar las citas: {str(e)}"
        )