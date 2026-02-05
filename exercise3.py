from datetime import date, time
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

# MongoDB corriendo en Docker o local
mongo_client = MongoClient("mongodb://localhost:27017/")

# Base de datos
database = mongo_client["eventify_db"]
clients_collection = database["clients"]
events_collection = database["events"]

# Limpiar colecciones (solo para demo)
clients_collection.delete_many({})
events_collection.delete_many({})

# Índice único para email (equivalente a UNIQUE en SQL)
clients_collection.create_index("email", unique=True)

# El crud de clientes
def create_client(client_name: str, client_email: str, client_phone: str):
    client_document = {
        "name": client_name,
        "email": client_email,
        "phone": client_phone
    }

    # Se prueba que el email no exista
    try:
        result = clients_collection.insert_one(client_document)
        client_document["_id"] = result.inserted_id
        return client_document

    except DuplicateKeyError:
        print("Error: el email ya existe")
        return None


def get_client_by_email(client_email: str):
    return clients_collection.find_one({"email": client_email})


def update_client_phone(client_email: str, new_phone: str):
    result = clients_collection.update_one(
        {"email": client_email},
        {"$set": {"phone": new_phone}}
    )
    return result.modified_count > 0


def delete_client(client_email: str):
    result = clients_collection.delete_one({"email": client_email})
    return result.deleted_count > 0

# Funciones para eventos
def create_event(
    event_name: str,
    event_description: str | None,
    start_date: date,
    venue: str,
    capacity: int
):
    event_document = {
        "name": event_name,
        "description": event_description,
        "start_date": start_date.isoformat(),  # Mongo no guarda date nativo, por lo que se usa el formato iso
        "start_time": time(20, 0).isoformat(),
        "venue": venue,
        "capacity": capacity
    }

    result = events_collection.insert_one(event_document)
    event_document["_id"] = result.inserted_id
    return event_document


def list_events():
    return list(events_collection.find())

# Demostración de las funciones
if __name__ == "__main__":
    # 1. Crear cliente
    print("\n1.Creando cliente...")
    client = create_client("Juan", "juan@gmail.com", "4425896310")
    if client:
        print("Cliente creado:")
        print("Nombre:", client['name'] + ", Correo:", client['email'] + ", Telefono:", client['phone'])

    # 2. Buscar cliente por email
    print("\n2.Buscando cliente por email...")
    found_client = get_client_by_email("juan@gmail.com")
    print("Resultado:")
    print("Nombre:", found_client['name'] + ", Correo:", found_client['email'] + ", Telefono:", found_client['phone'])

    # 3. Actualizar teléfono
    print("\n3.Actualizando teléfono...")
    if update_client_phone("juan@gmail.com", "4420000000"):
        updated = get_client_by_email("juan@gmail.com")
        print("Teléfono actualizado:", updated["phone"])

    # 4. Crear evento (Concierto X)
    print("\n4.Registrando evento...")
    event = create_event(
        "Concierto X",
        None,
        date(2026, 6, 15),
        "Auditorio Nacional",
        1650
    )
    print("Evento creado:", event)

    # 5. Crear evento (Concierto Z)
    print("\n5.Registrando otro evento...")
    event = create_event(
        "Concierto Z",
        None,
        date(2026, 6, 15),
        "Plaza de Toros",
        2000
    )
    print("Evento creado:", event)

    # 6. Listar eventos
    print("\n6.Listando todos los eventos...")
    for evento in list_events():
        print(f" - {evento['name']}, {evento['venue']}, {evento['start_date']}")

    # 7. Eliminar cliente
    print("\n7.Eliminando cliente...")
    if delete_client("juan@gmail.com"):
        print("Cliente eliminado")

    # 8. Verificar eliminación
    print("\n8.Verificando cliente eliminado...")
    print(get_client_by_email("juan@gmail.com"))
