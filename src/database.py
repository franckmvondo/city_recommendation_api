# /usr/bin/env python3
# coding: utf-8


from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
from typing import Any
from unidecode import unidecode


import io
import pandas as pd
import requests


############### Setting Database
# create engine to connect to database
engine = create_engine("sqlite:///./database.db")

db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

Base: Any = declarative_base()
Base.query = db_session.query_property()


class Cities(Base):
    __tablename__ = "cities"
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_zone = Column(String)
    insee_code = Column(String)
    libgeo = Column(String)
    department_code = Column(String)
    average_rent_per_m2 = Column(Float)
    note = Column(Float)
    population = Column(Integer)
    zip_code = Column(String)

    def __init__(
        self, id_zone, insee_code, libgeo, department_code, average_rent_per_m2
    ):
        self.id_zone = id_zone
        self.insee_code = insee_code
        self.libgeo = libgeo
        self.department_code = department_code
        self.average_rent_per_m2 = average_rent_per_m2

    def __repr__(self):
        return f"""<City(
            id_zone='{self.id_zone}',
            insee_code='{self.insee_code}',
            libgeo='{self.libgeo}',
            department_code='{self.department_code}',
            average_rent_per_m2='{self.average_rent_per_m2}')>"""


def get_all_insee_code() -> pd.DataFrame:
    url = "https://www.data.gouv.fr/fr/datasets/r/bc9d5d13-07cc-4d38-8254-88db065bd42b"
    response = requests.get(url)
    decoded_content = response.content.decode("ISO-8859-1")
    df = pd.read_csv(io.StringIO(decoded_content), delimiter=";")
    columns_to_drop = [
        "REG",
        "EPCI",
        "TYPPRED",
        "lwr.IPm2",
        "upr.IPm2",
        "R2_adj",
        "nbobs_mail",
        "nbobs_com",
    ]
    df = df.drop(columns_to_drop, axis=1)

    df["LIBGEO"] = (
        df["LIBGEO"]
        .str.replace("La ", "")
        .str.replace("Le ", "")
        .str.replace("Les ", "")
        .str.replace("L'", "")
        .str.replace("D'", "d-")
        .str.replace("d'", "d-")
        .str.replace("l'", "l-")
        .str.replace(" ", "-")
    )

    df["loypredm2"] = df["loypredm2"].str.replace(",", ".")
    df["INSEE_C"] = df["INSEE_C"].apply(lambda x: "0" + x if len(x) == 4 else x)
    df["loypredm2"] = df["loypredm2"].apply(lambda x: float(x))

    df.columns = [
        "id_zone",
        "insee_code",
        "libgeo",
        "department_code",
        "average_rent_per_m2",
    ]
    return df


def init_db():
    Base.metadata.create_all(engine)
    df = get_all_insee_code()
    df.to_sql("cities", engine, if_exists="append", index=False)


def update_db():
    cities = Cities.query.all()
    for city in cities:
        city_details = get_city_details(city.insee_code)
        if city_details is not None:
            city.note = get_note(city.insee_code, city.libgeo)
            city.zip_code = city_details.get("codesPostaux")[0]
            city.population = city_details.get("population")
            db_session.commit()


def get_city_details(insee_code: str):
    city_details: None
    url = f"https://geo.api.gouv.fr/communes/{insee_code}"
    response = requests.get(url)
    if response.status_code == 200:
        city_details = response.json()
    return city_details


def get_city_detailsEx(department_code: str):
    city_details = None
    url = f"https://geo.api.gouv.fr/departements/{department_code}/communes"
    response = requests.get(url)
    if response.status_code == 200:
        city_details = response.json()
    return city_details


def get_note(insee_code: str, libgeo: str):
    note = None
    url = f"https://www.bien-dans-ma-ville.fr/{unidecode(libgeo).lower()}-{insee_code}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        note = soup.find("div", {"class": "bloc_notemoyenne"}).find(
            "div", {"class": "total"}
        )
        if note is not None:
            note = note.text
    return note
