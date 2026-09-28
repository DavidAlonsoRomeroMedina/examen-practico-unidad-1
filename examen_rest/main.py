import time

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine, get_db
from models import Laptop


class LaptopCreate(BaseModel):
    marca: str
    modelo: str
    ram_gb: int


def laptop_a_dict(laptop):
    return {
        "id": laptop.id,
        "marca": laptop.marca,
        "modelo": laptop.modelo,
        "ram_gb": laptop.ram_gb,
        "disponible": bool(laptop.disponible),
    }


def cargar_datos():
    intentos = 0
    while intentos < 30:
        try:
            Base.metadata.create_all(bind=engine)
            db = SessionLocal()
            try:
                if db.query(Laptop).count() == 0:
                    db.add(
                        Laptop(
                            marca="Dell",
                            modelo="Latitude 5440",
                            ram_gb=16,
                            disponible=True,
                        )
                    )
                    db.add(
                        Laptop(
                            marca="Lenovo",
                            modelo="ThinkPad E14",
                            ram_gb=8,
                            disponible=False,
                        )
                    )
                    db.add(
                        Laptop(
                            marca="HP",
                            modelo="ProBook 450",
                            ram_gb=16,
                            disponible=True,
                        )
                    )
                    db.commit()
            finally:
                db.close()
            return
        except OperationalError:
            engine.dispose()
            intentos = intentos + 1
            time.sleep(3)
    raise RuntimeError("MySQL no acepto la conexion")


app = FastAPI()


@app.on_event("startup")
def startup():
    cargar_datos()


@app.get("/")
def inicio():
    return {"mensaje": "API del laboratorio de cómputo"}


@app.get("/laptops")
def listar_laptops(db: Session = Depends(get_db)):
    laptops = db.query(Laptop).order_by(Laptop.id).all()
    return [laptop_a_dict(laptop) for laptop in laptops]


@app.get("/laptops/disponibles")
def listar_disponibles(db: Session = Depends(get_db)):
    laptops = (
        db.query(Laptop)
        .filter(Laptop.disponible == True)
        .order_by(Laptop.id)
        .all()
    )
    return [laptop_a_dict(laptop) for laptop in laptops]


@app.get("/laptops/{laptop_id}")
def consultar_laptop(laptop_id: int, db: Session = Depends(get_db)):
    laptop = db.query(Laptop).filter(Laptop.id == laptop_id).first()
    if laptop is None:
        raise HTTPException(status_code=404, detail="Laptop no encontrada")
    return laptop_a_dict(laptop)


@app.post("/laptops")
def crear_laptop(datos: LaptopCreate, db: Session = Depends(get_db)):
    laptop = Laptop(
        marca=datos.marca,
        modelo=datos.modelo,
        ram_gb=datos.ram_gb,
        disponible=True,
    )
    db.add(laptop)
    db.commit()
    db.refresh(laptop)
    return laptop_a_dict(laptop)
