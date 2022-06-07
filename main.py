#Python
from typing import Optional
from enum import Enum # Enumeraciones de strings

#Pydantic
from pydantic import BaseModel
from pydantic import Field
from pydantic import EmailStr

#FastAPI
from fastapi import FastAPI
from fastapi import status
from fastapi import HTTPException
from fastapi import Body, Query, Path, Form, Header, Cookie, UploadFile, File

app = FastAPI()

# Models

class HairColor(Enum):
    white = 'white'
    brown = 'brown'
    black = 'black'
    blonde = 'blonde'
    red = 'red'
class Location(BaseModel):
    city: str = Field(
        min_length=1,
        max_length= 10,
        example="Bogota"
        )
    state: str = Field(
        min_length=1,
        max_length= 10,
        example="Cundinamarca"
        )
    country: str = Field(
        min_length=1,
        max_length= 10,
        example="Colombia"
        ) #los examples no funcionan con la clase de config
class PersonBase(BaseModel):
    first_name: str = Field( #validar Class parameters
        ...,
        min_length = 1,
        max_length = 50,
        ) #puedo poner ejemplos dentro del Field pero con la clase de config queda bien
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
    class Config:
        schema_extra = {
            "example": {
                "first_name": "Juan",
                "last_name": "Rico",
                "age": 30,
                "hair_color": "blonde",
                "is_married": False,
                "password" : "1234ag678"
            }
        }
class Person(PersonBase):
    password: str = Field(..., min_length = 8)
class PersonOut(PersonBase):
    pass

# Database
people = [1, 2, 3, 4, 5]
class LoginOut(BaseModel):
    username: str = Field(..., max_length = 20, example = "judricomo")
    message: str = Field(default="Login Succesfully!")

@app.get(
    path= "/",
    status_code=status.HTTP_200_OK,
    tags =["Home"]
    )
def home():
    return {"Hello": "World"}

# Request and Response Body

@app.post(
    path= "/person/new",
    response_model = PersonOut,
    status_code = status.HTTP_201_CREATED,
    tags =["Person"],
    summary = "Create a new person in the app"
    ) # con response model devuelvo lo que esta en PersonOut
def create_person(
    person: Person = Body(...)
    ):
    """
    Create Person
    This path operation creates a person in the app and save the information in the database

    Parameters:
    - Request body parameter:
        - **person: Person** -> A person model with first name, last name, age, hair color and marital stauts

    Returns a person model with first name, last name, age, hair color and marital status
    """
    return person

# Validaciones: Query Parameters

@app.get(
    path = "/person/detail",
    status_code=status.HTTP_200_OK,
    tags =["Person"],
    summary ="Query person's name and age"
    )
def show_person(
    #default is none for query parameters min lenght 1 max lenght 50
    name : Optional[str] = Query(
        None,
        min_length = 1,
        max_length = 50,
        title = "Person Name",
        description = "This is the person name. It is between 1 and 50 characters long",
        example = "Andrea"
        ),
    age : str = Query(
        ..., #significa que es requerido
        title="Person Age",
        description="This is the person age. It is required",
        example="30"
        )
    ):
    return {name: age}

#Validaciones: Path Parameters

@app.get(
    path = "/person/detail/{person_id}",
    status_code =status.HTTP_200_OK,
    tags =["Person"]
    )
def show_person(
    person_id : int = Path(
            ...,
            gt = 0,
            title = "Person ID",
            description = "This is the person ID must be greater than 0",
            example = 120
            )
    ):
    """

    """
    if person_id not in people:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "This person has not been registered!"
        ) ## raise is used instead of return when conditions are set
    return {person_id: "It exists!!"}

# Validaciones:Request Body

@app.put(
    path="/person/{person_id}",
    status_code=status.HTTP_202_ACCEPTED,
    tags =["Person"]
    )
def update_person(
    person_id: int = Path(
        ...,
        title = "Person ID",
        description = "This is the person ID",
        gt = 0,
        example = 123
    ),
    person: PersonOut = Body(...), #las validaciones de request bodies se hacen setenando los parametros del modelo de pydantic
    #location: Location = Body(...),
):
    #results = person.dict()
    #results.update(location.dict())
    #return results
    return person

#Forms

@app.post(
    path = "/login",
    response_model = LoginOut,
    status_code=status.HTTP_200_OK,
    tags =["Person"]
)
def login(
    username: str = Form(...),
    password: str = Form(...)):
    return LoginOut(username = username)

# Cookies and headers

@app.post(
    path="/contact",
    status_code=status.HTTP_200_OK,
    tags =["Contact"]
)
def contact(
    first_name: str = Form(
        ...,
        max_length=20,
        min_length=1,
        example ="Juan"
    ),
    last_name: str = Form(
        ...,
        max_length=20,
        min_length=1,
        example="Rico"
    ),
    email: EmailStr = Form(...),
    message: str = Form(
        ...,
        min_length=20,
        example = "quiero recibir informacion sobre los productos que estan ofreciendo"
    ),
    user_agent: Optional[str] = Header(default=None),
    ads: Optional[str] = Cookie(default=None)
):
    return user_agent

# Files

@app.post(
    path="/post-image",
    tags =["File"]
    )
def post_image(
    image : UploadFile = File(...)
):
    return{
        "Filename" : image.filename,
        "Format" : image.content_type,
        "Size(kb)": round(len(image.file.read())/ 1024)
    }