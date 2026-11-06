"""Crea o busca un usuario mediante tai-api."""

import os
from database.public import UsuarioCreate
import requests


api_url = os.getenv("TAI_API_URL", "http://localhost:8000")
token = os.getenv("TAI_API_TOKEN", "")
cabeceras = {}
if token:
    cabeceras["Authorization"] = "Bearer " + token

opcion = input("¿Desea crear o recuperar un usuario? (c/r): ").strip().lower()

if opcion == "c":
    usuario = UsuarioCreate(
        nombre=input("Introduce el nombre del usuario: "),
        apellido=input("Introduce el apellido del usuario: "),
        email=input("Introduce el email del usuario: "),
    )

    respuesta = requests.post(
        api_url + "/public/usuario",
        json=usuario.model_dump(exclude_none=True),
        headers=cabeceras,
    )
elif opcion == "r":
    email = input("Introduce el email del usuario a recuperar: ")

    respuesta = requests.get(
        api_url + "/public/usuario/find-by",
        params={"email": email},
        headers=cabeceras,
    )
else:
    print("Opción no válida. Escribe c para crear o r para recuperar.")
    raise SystemExit(1)

if not respuesta.ok:
    print("Error de tai-api:", respuesta.status_code, respuesta.text)
    raise SystemExit(1)

print(respuesta.json()["data"])
