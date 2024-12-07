import shutil
import json
from fastapi.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import pandas as pd
from typing import List, Optional
from pydantic import BaseModel as PydanticBaseModel

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
    dueños = load_data(file_path)
    mascotas = load_data(file_path_mascotas)
    citas = load_data(citas_path)
    facturas = load_data(facturas_path)

    # Calcular estadísticas generales
    total_dueños = len(dueños)
    total_mascotas = len(mascotas)
    total_citas = len(citas)
    total_ingresos = sum(factura.get("precio", 0) for factura in facturas)
    total_recibos = len(facturas)

    # Calcular ingresos por dueño
    ingresos_por_dueño = {}
    for factura in facturas:
        nombre_dueño = factura.get("nombre_dueño")
        if nombre_dueño:
            ingresos_por_dueño[nombre_dueño] = ingresos_por_dueño.get(nombre_dueño, 0) + factura.get("precio", 0)

    return {
        "dueños": total_dueños,
        "mascotas": total_mascotas,
        "citas": total_citas,
        "ingresos": total_ingresos,
        "recibos": total_recibos,
        "nombres_dueños": list(ingresos_por_dueño.keys()),  # Nombres de dueños
        "ingresos_por_dueño": list(ingresos_por_dueño.values()),  # Ingresos correspondientes
    }



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

@app.post("/registro_cita/")
async def registro_cita(data: FormDataCitas):
    # Validar que el dueño y la mascota existen
    try:
        with open(file_path, "r") as file:
            dueños = json.load(file)
        with open(file_path_mascotas, "r") as file:
            mascotas = json.load(file)

        dueño_valido = any(d["Nombre"] == data.Nombre_dueño for d in dueños)
        mascota_valida = any(
            m["Nombre"] == data.Nombre_mascota and m["Dueño"] == data.Nombre_dueño
            for m in mascotas
        )

        if not dueño_valido:
            raise HTTPException(status_code=400, detail="El dueño no existe.")
        if not mascota_valida:
            raise HTTPException(status_code=400, detail="La mascota no está asociada al dueño.")

    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Archivos de dueños o mascotas no encontrados.")

    # Guardar la cita
    citas_registradas = []
    try:
        with open(citas_path, "r") as file:
            citas_registradas = json.load(file)
    except FileNotFoundError:
        citas_registradas = []

    citas_registradas.append(data.dict())
    with open(citas_path, "w") as file:
        json.dump(citas_registradas, file, indent=4)

    return {"message": "Cita registrada con éxito"}

@app.get("/get_dueños/")
async def get_duenos():
    try:
        with open(file_path, "r") as file:
            dueños = json.load(file)
        return {"dueños": dueños}
    except FileNotFoundError:
        return {"dueños": []}

@app.get("/get_mascotas/")
async def get_mascotas():
    try:
        with open(file_path_mascotas, "r") as file:
            mascotas = json.load(file)
        return {"mascotas": mascotas}
    except FileNotFoundError:
        return {"mascotas": []}

@app.get("/get_citas/")
async def get_citas():
    try:
        with open(citas_path, "r") as file:
            citas = json.load(file)
        return {"citas": citas}
    except FileNotFoundError:
        return {"citas": []}

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

@app.post("/generar_factura/")
async def generar_factura(data: Factura):
    facturas = load_data(facturas_path)
    facturas.append(data.dict())
    save_data(facturas_path, facturas)
    return {"message": "Factura generada con éxito"}