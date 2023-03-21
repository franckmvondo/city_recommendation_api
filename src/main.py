# /usr/bin/env python3
# coding: utf-8

from .database import init_db, get_note, get_city_detailsEx, Cities

from fastapi import FastAPI
from unidecode import unidecode


app = FastAPI()

try:
    init_db()
except Exception as e:
    print(f"Erreur dans la tâche : {e}")


@app.get("/")
async def Home() -> dict:
    return {"Hello": "World"}


@app.get("/cities_recommendation/")
async def cities_recommendation(
    department_code: str, area: float, rent: float
) -> list[dict]:
    city_list = []
    rent_per_m2 = rent / area

    citiesEx = get_city_detailsEx(department_code)
    if citiesEx:
        for element in citiesEx:
            city = Cities.query.filter_by(insee_code=element["code"]).first()
            if city:
                note = get_note(city.insee_code, city.libgeo)
                if city.average_rent_per_m2 <= rent_per_m2:
                    city_dict = {
                        "Nom de ville": city.libgeo,
                        "Code Postale": element["codesPostaux"],
                        "Loyer moyen": city.average_rent_per_m2 * area,
                        "Note globale": note,
                        "Population": element["population"],
                    }
                    city_list.append(city_dict)

    return city_list
