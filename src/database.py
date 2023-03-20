# /usr/bin/env python3
# coding: utf-8


from typing import Any

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

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
    city_id = Column(Integer, primary_key=True, autoincrement=True)
    city_id_zone = Column(String)
    city_insee = Column(String)
    city_libgeo = Column(String)
    city_department_code = Column(String)
    city_average_rent_per_m2 = Column(Float)
    city_note = Column(Float)
    city_population = Column(Integer)

    def __init__(
        self,
        city_id_zone,
        city_insee,
        city_libgeo,
        city_department_code,
        city_average_rent_per_m2,
    ):
        self.city_id_zone = city_id_zone
        self.city_insee = city_insee
        self.city_libgeo = city_libgeo
        self.city_department_code = city_department_code
        self.city_average_rent_per_m2 = city_average_rent_per_m2

    def __repr__(self):
        return f"""<City(
            city_id_zone='{self.city_id_zone}',
            city_insee='{self.city_insee}',
            city_libgeo='{self.city_libgeo}',
            city_department_code='{self.city_department_code}',
            city_average_rent_per_m2='{self.city_average_rent_per_m2}')>"""


def get_all_insee() -> pd.DataFrame:
    url = "https://www.data.gouv.fr/fr/datasets/r/bc9d5d13-07cc-4d38-8254-88db065bd42b"
    response = requests.get(url)
    decoded_content = response.content.decode("ISO-8859-1")
    df = pd.read_csv(io.StringIO(decoded_content), delimiter=";")
    df = df.drop("REG", axis=1)
    df = df.drop("EPCI", axis=1)
    df = df.drop("TYPPRED", axis=1)
    df = df.drop("lwr.IPm2", axis=1)
    df = df.drop("upr.IPm2", axis=1)
    df = df.drop("R2_adj", axis=1)
    df = df.drop("nbobs_mail", axis=1)
    df = df.drop("nbobs_com", axis=1)

    df["LIBGEO"] = df["LIBGEO"].str.replace("La ", "")
    df["LIBGEO"] = df["LIBGEO"].str.replace("Le ", "")
    df["LIBGEO"] = df["LIBGEO"].str.replace("Les ", "")
    df["LIBGEO"] = df["LIBGEO"].str.replace("L'", "")
    df["LIBGEO"] = df["LIBGEO"].str.replace("D'", "d-")
    df["LIBGEO"] = df["LIBGEO"].str.replace("d'", "d-")
    df["LIBGEO"] = df["LIBGEO"].str.replace("l'", "l-")
    df["LIBGEO"] = df["LIBGEO"].str.replace(" ", "-")
    df["loypredm2"] = df["loypredm2"].str.replace(",", ".")
    df["INSEE_C"] = df["INSEE_C"].apply(lambda x: "0" + x if len(x) == 4 else x)
    df["loypredm2"] = df["loypredm2"].apply(lambda x: float(x))

    df.columns = [
        "city_id_zone",
        "city_insee",
        "city_libgeo",
        "city_department_code",
        "city_average_rent_per_m2",
    ]
    return df


def init_db():
    Base.metadata.create_all(engine)
    df = get_all_insee()
    df.to_sql("cities", engine, if_exists="append", index=False)
