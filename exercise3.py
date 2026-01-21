from sqlalchemy import create_engine, Column, Integer, String, Date, Time, text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import date, time
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

raw_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

# Codificar la contraseña (esto convertirá el '@' en '%40' de la contraseña)
safe_password = quote_plus(raw_password)

# Se construye el connection string a partir de la contraseña y el nombre de mi base de datos que se encuentran en el .env.
# Como profesor, puede reemplazar "{safe_password}" por su contraseña y "{db_name}" por el nombre de la suya para correr el programa.
# Claro que la contraseña tiene que ser la de su PostgreSQL, y el nombre tiene que ser igual a una que haya creado, preferentemente nueva.
DATABASE_URL = f"postgresql://postgres:{safe_password}@localhost:5432/{db_name}"

Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Clases
class Client(Base):
    __tablename__ = 'cliente'
    id_cliente = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(200), nullable=False, unique=True)
    telefono = Column(String(10), nullable=False)

    def __repr__(self):
        return f"<Client(id={self.id_cliente}, nombre='{self.nombre}', correo='{self.correo}')>"

class Event(Base):
    __tablename__ = 'evento'
    id_evento = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(350))
    fecha_inicio = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    lugar = Column(String(125), nullable=False)
    capacidad = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Event(id={self.id_evento}, nombre='{self.nombre}', lugar='{self.lugar}')>"

# Funciones del CRUD

# Funciones de Clientes
def create_client(name, email, phone):
    new_client = Client(nombre=name, correo=email, telefono=phone)
    session.add(new_client)
    try:
        session.commit()
        return new_client
    except Exception as e:
        session.rollback()
        print(f"Error al crear cliente: {e}")
        return None

def get_client_by_email(email):
    return session.query(Client).filter_by(correo=email).first()

def update_client_phone(email, new_phone):
    client = get_client_by_email(email)
    if client:
        client.telefono = new_phone
        session.commit()
        return True
    return False

def delete_client(email):
    client = get_client_by_email(email)
    if client:
        session.delete(client)
        session.commit()
        return True
    return False

# Funciones de Eventos
def create_event(name, desc, start_at, venue, capacity):
    #se añade una hora por defecto para cumplir con el esquema del MER
    new_event = Event(
        nombre=name,
        descripcion=desc,
        fecha_inicio=start_at,
        hora_inicio=time(20, 0),
        lugar=venue,
        capacidad=capacity
    )
    session.add(new_event)
    session.commit()
    return new_event

def list_events():
    return session.query(Event).all()


if __name__ == "__main__":
    # Esto crea las tablas si no existen
    Base.metadata.create_all(engine)

    print("--- Demostración del CRUD con PostgreSQL ---")

    # 1. Crear Cliente
    print("\n1. Creando cliente...")
    c = create_client("Juan", "juan@gmail.com", "4425896310")
    if c: print(f"Éxito: {c}")

    # 2. Consultar por Email
    print("\n2. Buscando cliente 'juan@gmail.com'...")
    found = get_client_by_email("juan@gmail.com")
    if found:
        print(f"Resultado: {found.nombre} | Teléfono: {found.telefono}")

    # 3. Actualizar
    print("\n3. Actualizando teléfono...")
    if update_client_phone("juan@gmail.com", "4420000000"):
        print("Teléfono actualizado correctamente.")
        print(f"Nuevo teléfono: {found.telefono}")

    # 4. Crear Evento (Concierto X)
    print("\n4. Registrando nuevo evento...")
    e = create_event("Concierto X", None, date(2026, 6, 15), "Auditorio Nacional", 1650)
    print(f"Evento registrado: {e.nombre} en {e.lugar}")

    # 5. Crear Evento (Concierto Z)
    print("\n5. Registrando nuevo evento...")
    e = create_event("Concierto Z", None, date(2026, 6, 15), "Plaza de Toros", 2000)
    print(f"Evento registrado: {e.nombre} en {e.lugar}")

    # 6. Listar todos
    print("\n6. Listado de eventos en BD:")
    eventos = list_events()
    for ev in eventos:
        print(f" - ID: {ev.id_evento} | {ev.nombre} ({ev.fecha_inicio})")

    # 7. Eliminar
    print("\n7. Eliminando cliente...")
    if delete_client("juan@gmail.com"):
        print("Cliente 'juan@gmail.com' eliminado.")

    # 8. Verificar que no existe
    print("\n8. Verificar que el cliente se haya eliminado...")
    print(get_client_by_email("juan@gmail.com"))