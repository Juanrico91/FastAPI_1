#Python
from typing import Optional
from enum import Enum # Enumeraciones de strings

#Pydantic
from pydantic import BaseModel, Field

#FastAPI
from fastapi import FastAPI
from fastapi import Body, Query, Path

app = FastAPI()

# Models

class HairColor(Enum):
    white = 'white'
    brown = 'brown'
    black = 'black'
    blonde = 'blonde'
    red = 'red'

class Location(BaseModel):
    city: str
    state: str
    country: str

class Person(BaseModel): 
    first_name: str = Field( #validar Class parameters
        ...,
        min_length = 1,
        max_length = 50,
        )
    last_name: str = Field(
        ...,
        min_length = 1,
        max_length = 50,
        )
    age: int = Field(
        ...,
        gt = 0,
        le = 115
    )
    hair_color: Optional[HairColor] = Field(default = None) #obligo a hair_color a ser heredado de la clase HairColor para tener los colores de validaciones
    is_married: Optional[bool] = Field(default = None)

@app.get("/")
def home(): 
    return {"Hello": "World"}

# Request and Response Body

@app.post("/person/new")
def create_person(person: Person = Body(...)): 
    return person

# Validaciones: Query Parameters

@app.get("/person/detail")
def show_person(
    #default is none for query parameters min lenght 1 max lenght 50
    name : Optional[str] = Query(
        None,
        min_length = 1,
        max_length = 50,
        title = "Person Name",
        description = "This is the person name. It is between 1 and 50 characters long"
        ),
    age : str = Query(
        ..., #significa que es requerido
        title="Person Age",
        description="This is the person age. It is required"
        )
):
    return {name: age}

#Validaciones: Path Parameters

@app.get("/person/detail/{person_id}")
def show_person(
    person_id : int = Path(
            ...,
            gt = 0,
            title = "Person Age",
            description = "This is the person age must be greater than 0")
):
    return {person_id: "It exists!!"}

# Validaciones:Request Body

@app.put("/person/{person_id}")
def update_person(
    person_id: int = Path(
        ...,
        title = "Person ID",
        description = "This is the person ID",
        gt = 0
    ),
    person: Person = Body(...), #las validaciones de request bodies se hacen setenando los parametros del modelo de pydantic
    location: Location = Body(...),
):
    results = person.dict()
    results.update(location.dict())
    return results