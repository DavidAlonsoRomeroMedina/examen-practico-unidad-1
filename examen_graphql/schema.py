import typing

import strawberry


@strawberry.type
class Instructor:
    nombre: str


@strawberry.type
class Taller:
    nombre: str
    instructor: Instructor
    cupo: int
    activo: bool


talleres_db = [
    Taller(
        nombre="Python para backend",
        instructor=Instructor(nombre="Ana López"),
        cupo=20,
        activo=True,
    ),
    Taller(
        nombre="Introducción a Docker",
        instructor=Instructor(nombre="Carlos Ruiz"),
        cupo=15,
        activo=False,
    ),
    Taller(
        nombre="Consultas con GraphQL",
        instructor=Instructor(nombre="Ana López"),
        cupo=25,
        activo=True,
    ),
]


def get_talleres():
    return talleres_db


@strawberry.type
class Query:
    talleres: typing.List[Taller] = strawberry.field(resolver=get_talleres)

    @strawberry.field
    def taller(self, nombre: str) -> typing.Optional[Taller]:
        for item in talleres_db:
            if item.nombre == nombre:
                return item
        return None

    @strawberry.field
    def talleres_activos(self) -> typing.List[Taller]:
        result = []
        for item in talleres_db:
            if item.activo:
                result.append(item)
        return result


@strawberry.input
class AgregarTallerInput:
    nombre: str
    instructor: str
    cupo: int
    activo: bool


@strawberry.type
class Mutation:
    @strawberry.mutation
    def agregar_taller(self, taller: AgregarTallerInput) -> Taller:
        nuevo = Taller(
            nombre=taller.nombre,
            instructor=Instructor(nombre=taller.instructor),
            cupo=taller.cupo,
            activo=taller.activo,
        )
        talleres_db.append(nuevo)
        return nuevo


schema = strawberry.Schema(query=Query, mutation=Mutation)
