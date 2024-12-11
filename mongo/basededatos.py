from pymongo import MongoClient
from typing import List, Optional
from datetime import datetime

class BaseDeDatos:
    def __init__(self):
        # Usar el nombre del servicio definido en docker-compose.yml
        self.client = MongoClient('mongodb://mongodb:27017/')
        self.db = self.client.clinica_veterinaria

    # Operaciones para Dueños
    async def crear_dueno(self, dueno_data: dict) -> dict:
        resultado = self.db.duenos.insert_one(dueno_data)
        dueno_data['_id'] = str(resultado.inserted_id)
        return dueno_data

    async def obtener_duenos(self) -> List[dict]:
        try:
            # Convertir el cursor a lista directamente
            duenos = list(self.db.duenos.find({}))
            # Convertir ObjectId a string y procesar los resultados
            for dueno in duenos:
                dueno['_id'] = str(dueno['_id'])
            print(f"Dueños encontrados: {duenos}")  # Debug log
            return duenos
        except Exception as e:
            print(f"Error al obtener dueños: {str(e)}")
            return []

    async def buscar_dueno(self, nombre: str) -> Optional[dict]:
        return self.db.duenos.find_one({'Nombre': nombre}, {'_id': 0})

    async def eliminar_dueno(self, nombre_dueño: str) -> bool:
        try:
            resultado = self.db.duenos.delete_one({'Nombre': nombre_dueño})
            print(f"Dueño eliminado: {resultado.deleted_count}")  # Debug log
            return resultado.deleted_count > 0
        except Exception as e:
            print(f"Error al eliminar dueño: {str(e)}")  # Debug log
            return False

    # Operaciones para Mascotas
    async def crear_mascota(self, mascota_data: dict) -> dict:
        try:
            # Validar que los campos requeridos estén presentes y no estén vacíos
            campos_requeridos = ["nombre_mascota", "nombre_dueño", "tipo", "edad"]
            for campo in campos_requeridos:
                if campo not in mascota_data or not str(mascota_data[campo]).strip():
                    raise ValueError(f"El campo {campo} es requerido y no puede estar vacío")
            
            # Limpiar espacios en blanco de los campos de texto
            for campo in ["nombre_mascota", "nombre_dueño", "tipo", "raza"]:
                if campo in mascota_data and isinstance(mascota_data[campo], str):
                    mascota_data[campo] = mascota_data[campo].strip()
            
            print(f"Intentando crear mascota con datos: {mascota_data}")
            resultado = self.db.mascotas.insert_one(mascota_data)
            mascota_data['_id'] = str(resultado.inserted_id)
            return mascota_data
        except Exception as e:
            print(f"Error al crear mascota: {str(e)}")
            raise

    async def obtener_mascotas(self) -> List[dict]:
        try:
            # Convertir el cursor a lista directamente
            mascotas = list(self.db.mascotas.find({}))
            # Convertir ObjectId a string y procesar los resultados
            for mascota in mascotas:
                mascota['_id'] = str(mascota['_id'])
            print(f"Mascotas encontradas: {mascotas}")  # Debug log
            return mascotas
        except Exception as e:
            print(f"Error al obtener mascotas: {str(e)}")
            return []

    async def obtener_mascotas_por_dueno(self, nombre_dueno: str) -> List[dict]:
        try:
            # Buscar mascotas por dueño
            mascotas = list(self.db.mascotas.find(
                {'nombre_dueño': nombre_dueno.strip()}, 
                {'_id': 0}
            ))
            
            # Filtrar y procesar resultados
            mascotas_procesadas = []
            for mascota in mascotas:
                if mascota.get('nombre_mascota') and mascota.get('tipo'):
                    mascotas_procesadas.append({
                        "Nombre": mascota['nombre_mascota'].strip(),
                        "Dueño": mascota['nombre_dueño'].strip(),
                        "Tipo": mascota['tipo'].strip()
                    })
            
            print(f"Mascotas encontradas para {nombre_dueno}: {mascotas_procesadas}")
            return mascotas_procesadas
        except Exception as e:
            print(f"Error al obtener mascotas: {str(e)}")
            return []

    async def eliminar_mascotas_por_dueno(self, nombre_dueño: str) -> bool:
        try:
            resultado = self.db.mascotas.delete_many({'nombre_dueño': nombre_dueño})
            print(f"Mascotas eliminadas: {resultado.deleted_count}")  # Debug log
            return resultado.deleted_count > 0
        except Exception as e:
            print(f"Error al eliminar mascotas: {str(e)}")  # Debug log
            return False

    # Operaciones para Citas
    async def crear_cita(self, cita_data: dict) -> dict:
        try:
            print(f"Creando cita con datos: {cita_data}")  # Debug log
            
            # Asegurarse de que las fechas están en el formato correcto
            if isinstance(cita_data["Fecha_inicio"], str):
                cita_data["Fecha_inicio"] = cita_data["Fecha_inicio"].replace("T", " ")
            if isinstance(cita_data["Fecha_fin"], str):
                cita_data["Fecha_fin"] = cita_data["Fecha_fin"].replace("T", " ")
            
            # Insertar la cita
            resultado = self.db.citas.insert_one(cita_data)
            cita_data["_id"] = str(resultado.inserted_id)
            
            print(f"Cita creada: {cita_data}")  # Debug log
            return cita_data
        except Exception as e:
            print(f"Error al crear cita: {str(e)}")
            raise

    async def obtener_citas(self) -> List[dict]:
        try:
            # Obtener todas las citas y convertir ObjectId a string
            citas = list(self.db.citas.find({}, {'_id': 0}))
            
            # Asegurarse de que las fechas están en el formato correcto
            for cita in citas:
                if isinstance(cita.get("Fecha_inicio"), str):
                    cita["Fecha_inicio"] = cita["Fecha_inicio"].replace(" ", "T")
                if isinstance(cita.get("Fecha_fin"), str):
                    cita["Fecha_fin"] = cita["Fecha_fin"].replace(" ", "T")
            
            print(f"Citas recuperadas: {citas}")  # Debug log
            return citas
        except Exception as e:
            print(f"Error al obtener citas: {str(e)}")
            return []

    # Operaciones para Facturas
    async def crear_factura(self, factura_data: dict) -> dict:
        try:
            resultado = self.db.facturas.insert_one(factura_data)
            factura_data['_id'] = str(resultado.inserted_id)
            return factura_data
        except Exception as e:
            print(f"Error al crear factura: {str(e)}")
            raise

    async def obtener_facturas(self) -> List[dict]:
        return list(self.db.facturas.find({}, {'_id': 0}))

    # Estadísticas
    async def obtener_estadisticas(self) -> dict:
        total_duenos = self.db.duenos.count_documents({})
        total_mascotas = self.db.mascotas.count_documents({})
        total_citas = self.db.citas.count_documents({})
        facturas = list(self.db.facturas.find({}, {'precio': 1, 'nombre_dueño': 1}))
        
        total_ingresos = sum(factura.get('precio', 0) for factura in facturas)
        ingresos_por_dueno = {}
        for factura in facturas:
            nombre_dueno = factura.get('nombre_dueño')
            if nombre_dueno:
                ingresos_por_dueno[nombre_dueno] = ingresos_por_dueno.get(nombre_dueno, 0) + factura.get('precio', 0)

        return {
            'dueños': total_duenos,
            'mascotas': total_mascotas,
            'citas': total_citas,
            'ingresos': total_ingresos,
            'recibos': len(facturas),
            'nombres_dueños': list(ingresos_por_dueno.keys()),
            'ingresos_por_dueño': list(ingresos_por_dueno.values())
        }

    async def limpiar_base_datos(self):
        try:
            print("Iniciando limpieza de la base de datos...")  # Debug log
            
            # Limpiar directamente las colecciones principales
            colecciones = ['mascotas', 'duenos', 'citas', 'facturas']
            
            for coleccion in colecciones:
                try:
                    resultado = self.db[coleccion].delete_many({})
                    print(f"Eliminados {resultado.deleted_count} documentos de {coleccion}")
                except Exception as e:
                    print(f"Error al limpiar colección {coleccion}: {str(e)}")
            
            # Verificación adicional
            for coleccion in colecciones:
                count = self.db[coleccion].count_documents({})
                print(f"Documentos restantes en {coleccion}: {count}")
            
            # Si todo está bien, devolver True
            return True
            
        except Exception as e:
            print(f"Error durante la limpieza de la base de datos: {str(e)}")
            raise

    async def limpiar_citas(self) -> bool:
        try:
            resultado = self.db.citas.delete_many({})
            print(f"Eliminadas {resultado.deleted_count} citas")  # Debug log
            return resultado.deleted_count >= 0
        except Exception as e:
            print(f"Error al limpiar citas: {str(e)}")  # Debug log
            return False
