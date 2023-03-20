# /usr/bin/env python3
# coding: utf-8

from .database import init_db, Cities

from fastapi import FastAPI


app = FastAPI()
init_db()


@app.get("/")
async def Home() -> dict:
    return {"Home": "Hello World"}


@app.get("/cities_recommendation/")
async def cities_recommendation(
    department_code: str,
    area: float,
    rent: float,
) -> list[dict]:
    city_list = []
    rent_per_m2 = rent / area
    cities = Cities.query.filter(
        Cities.city_department_code == department_code,
        Cities.city_average_rent_per_m2 <= rent_per_m2,
    ).all()
    for city in cities:
        city_dict = {
            "Nom de ville": city.city_libgeo,
            "Code Postale": city.city_insee,
            "Loyer moyen": city.city_average_rent_per_m2 * area,
            "Note globale": city.city_note,
            "Population": city.city_population,
        }
        city_list.append(city_dict)

    return city_list
